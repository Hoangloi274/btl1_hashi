import json
from environments.pipes_env import PipesEnvironment
from solvers.astar import a_star_search
from gui.pipes_gui import run_pipes_gui

def main():
    # 1. Đọc testcase
    with open("testcase/pipes_4x4.json", "r") as f:
        data = json.load(f)
    
    # 2. Khởi tạo môi trường
    env = PipesEnvironment(data)
    
    # 3. Chạy thuật toán tìm kiếm (ví dụ A*)
    print("Đang chạy thuật toán A* cho Pipes...")
    path, nodes_expanded = a_star_search(env)
    
    if path:
        print(f"Tìm thấy lời giải! Số bước: {len(path)}, Số nút đã duyệt: {nodes_expanded}")
        # 4. Truyền kết quả sang giao diện trực quan step-by-step
        run_pipes_gui(env, path)
    else:
        print("Không tìm thấy lời giải.")

if __name__ == "__main__":
    main()