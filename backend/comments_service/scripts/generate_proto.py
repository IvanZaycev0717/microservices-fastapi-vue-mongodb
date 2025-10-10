import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "src/proto"
    output_dir = project_root / "src/proto"

    output_dir.mkdir(parents=True, exist_ok=True)

    python_executable = sys.executable

    cmd = [
        python_executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        f"--pyi_out={output_dir}",
        str(proto_dir / "comments.proto"),
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, cwd=project_root)
        print("✅ Protobuf код успешно сгенерирован")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка генерации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()