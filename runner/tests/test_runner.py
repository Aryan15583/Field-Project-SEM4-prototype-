"""Run with: pytest runner   (needs gcc, g++, javac; the isolation tests need root, like the real container)."""
import os
import socket
import sys
import time

import pytest
from fastapi.testclient import TestClient

os.environ["RUNNER_KEY"] = "test-key"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import app as runner  # noqa: E402

client = TestClient(runner.app)
H = {"X-Runner-Key": "test-key"}

HELLO = {
    "c": '#include <stdio.h>\nint main(void){ int n; if(scanf("%d",&n)==1) printf("n=%d\\n",n); else printf("hello\\n"); return 0; }',
    "cpp": '#include <iostream>\nint main(){ int n; if(std::cin>>n) std::cout<<"n="<<n<<"\\n"; else std::cout<<"hello\\n"; }',
    "java": "import java.util.*;\npublic class Main { public static void main(String[] a){ Scanner s=new Scanner(System.in); if(s.hasNextInt()) System.out.println(\"n=\"+s.nextInt()); else System.out.println(\"hello\"); } }",
}


def run(language, code, stdins=("",), **kw):
    r = client.post("/api/v1/run", headers=H, json={"language": language, "code": code, "stdins": list(stdins), **kw})
    assert r.status_code == 200, r.text
    return r.json()


needs_root = pytest.mark.skipif(not runner.AS_ROOT, reason="isolation only exists when the runner starts as root (as it does in Docker)")


def test_key_is_required():
    assert client.post("/api/v1/run", json={"language": "c", "code": "int main(){}"}).status_code == 401
    assert client.post("/api/v1/run", headers={"X-Runner-Key": "nope"}, json={"language": "c", "code": "int main(){}"}).status_code == 401
    assert client.get("/api/health").json()["status"] == "ok"  # health needs no key (used to wake the service)


def test_unsupported_language():
    assert client.post("/api/v1/run", headers=H, json={"language": "ruby", "code": "puts 1"}).status_code == 400


@pytest.mark.parametrize("lang", ["c", "cpp", "java"])
def test_compile_once_run_many_inputs(lang):
    out = run(lang, HELLO[lang], ["", "42", "7"])
    assert out["compile"]["ok"]
    assert [r["stdout"].strip() for r in out["runs"]] == ["hello", "n=42", "n=7"]
    assert all(r["ok"] for r in out["runs"])


@pytest.mark.parametrize("lang", ["c", "cpp", "java"])
def test_compile_error_is_reported(lang):
    out = run(lang, "this is not a program")
    assert out["compile"]["ok"] is False and out["compile"]["stderr"] and out["runs"] == []


def test_runtime_failure_is_not_ok():
    out = run("c", "#include <stdlib.h>\nint main(void){ return 3; }")
    assert out["compile"]["ok"] and out["runs"][0]["ok"] is False
    out = run("java", "public class Main { public static void main(String[] a){ throw new RuntimeException(\"boom\"); } }")
    assert out["runs"][0]["ok"] is False and "boom" in out["runs"][0]["stderr"]


def test_infinite_loop_is_stopped():
    t = time.monotonic()
    out = run("c", "int main(void){ for(;;){} }", run_timeout_ms=1000)
    assert time.monotonic() - t < 15
    assert out["runs"][0]["ok"] is False and out["runs"][0]["signal"] and "Time limit" in out["runs"][0]["stderr"]


def test_endless_output_is_capped():
    out = run("c", '#include <stdio.h>\nint main(void){ for(;;) puts("spam spam spam spam"); }', run_timeout_ms=2000)
    assert len(out["runs"][0]["stdout"]) <= runner.MAX_OUTPUT and out["runs"][0]["ok"] is False


def test_memory_bomb_fails_without_hurting_the_service():
    out = run("c", "#include <stdlib.h>\n#include <string.h>\nint main(void){ for(;;){ char *p=malloc(50000000); if(!p) return 7; memset(p,1,50000000);} }", run_timeout_ms=4000)
    assert out["runs"][0]["ok"] is False
    assert run("c", HELLO["c"])["runs"][0]["stdout"].strip() == "hello"  # still healthy afterwards


def test_fork_bomb_is_contained():
    out = run("c", "#include <unistd.h>\nint main(void){ for(;;) fork(); }", run_timeout_ms=2000)
    assert out["runs"][0]["ok"] is False
    assert run("c", HELLO["c"])["runs"][0]["stdout"].strip() == "hello"


@needs_root
def test_program_cannot_read_the_runners_environment():
    # the key lives in this process's environment; a program started as "nobody" must not be able to read it
    code = (
        '#include <stdio.h>\n#include <stdlib.h>\nint main(int c, char**v){ char path[64]; snprintf(path,64,"/proc/%s/environ","' + str(os.getpid()) + '");'
        ' FILE*f=fopen(path,"r"); if(!f){ printf("DENIED\\n"); return 0;} char b[4096]; size_t n=fread(b,1,4095,f); b[n]=0; printf("READ:%s\\n", b); return 0; }'
    )
    out = run("c", code)["runs"][0]["stdout"]
    assert "DENIED" in out and "test-key" not in out


@needs_root
def test_program_cannot_hijack_the_output_files():
    # it tries to point the runner's output file at a secret via a symlink in its own directory
    secret = "/proc/%d/environ" % os.getpid()
    code = ('#include <unistd.h>\n#include <stdio.h>\nint main(void){ unlink(".run.out"); symlink("' + secret + '", ".run.out"); puts("done"); return 0; }')
    out = run("c", code)["runs"][0]["stdout"]
    assert "test-key" not in out


@pytest.mark.skipif(not runner.NETWORK_ISOLATED, reason="this host does not allow network namespaces (the runner reports it on /api/health)")
def test_program_has_no_network():
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)
    port = srv.getsockname()[1]
    code = ('#include <stdio.h>\n#include <arpa/inet.h>\n#include <sys/socket.h>\nint main(void){ int s=socket(AF_INET,SOCK_STREAM,0); struct sockaddr_in a={0};'
            ' a.sin_family=AF_INET; a.sin_port=htons(' + str(port) + '); inet_pton(AF_INET,"127.0.0.1",&a.sin_addr);'
            ' puts(connect(s,(struct sockaddr*)&a,sizeof a)==0 ? "CONNECTED" : "NO-NETWORK"); return 0; }')
    out = run("c", code)["runs"][0]["stdout"]
    srv.close()
    assert "NO-NETWORK" in out


def test_busy_runner_says_so(monkeypatch):
    monkeypatch.setattr(runner, "_waiting", runner.MAX_WAITING)
    assert client.post("/api/v1/run", headers=H, json={"language": "c", "code": "int main(){}"}).status_code == 429
