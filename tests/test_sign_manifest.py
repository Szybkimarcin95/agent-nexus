from release.sign_manifest import build_manifest, write_manifest, verify_manifest

def test_manifest_deterministic(tmp_path):
    assert build_manifest(tmp_path)["top_hash"] == build_manifest(tmp_path)["top_hash"]

def test_manifest_detects_change(tmp_path):
    f=tmp_path/"test.txt"; f.write_text("hello")
    m=tmp_path/"manifest.json"; write_manifest(tmp_path,m)
    assert verify_manifest(tmp_path,m)["ok"]
    f.write_text("tampered")
    assert verify_manifest(tmp_path,m)["ok"] is False

def test_manifest_role(tmp_path):
    assert build_manifest(tmp_path,"Supervisor")["role"]=="Supervisor"
