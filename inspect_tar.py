
import tarfile

tar_path = r"c:\Users\pahad\Desktop\AutoGen\data\img\9001695\20041228\00456208.tar.gz"

try:
    with tarfile.open(tar_path, "r:gz") as tar:
        print(f"Members: {[m.name for m in tar.getmembers()]}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
