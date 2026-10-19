# 


## 1. State Spaces & Search Problems (Không gian trạng thái & Bài toán Tìm kiếm)

Phần này hướng dẫn cách toán học hóa môi trường thực tế để một tác tử lập kế hoạch (planning agent) có thể tìm kiếm đường đi tối ưu đến mục tiêu.

### 1.1 6 Thành phần cấu thành một Bài toán Tìm kiếm (Search Problem)

Một bài toán tìm kiếm được định nghĩa chính xác bằng 6 yếu tố cốt lõi:

1. **Không gian trạng thái (State Space):** Tập hợp tất cả các trạng thái có thể xảy ra trong thế giới.
2. **Tập hợp các hành động (Actions):** Các hành động khả thi mà tác tử có thể chọn tại mỗi trạng thái.
3. **Mô hình chuyển trạng thái (Transition Model):** Hàm trả về trạng thái kế tiếp khi thực hiện một hành động từ trạng thái hiện tại.
4. **Chi phí hành động (Action Cost):** Chi phí phát sinh khi di chuyển từ trạng thái này sang trạng thái khác.
5. **Trạng thái bắt đầu (Start State):** Trạng thái xuất phát ban đầu của tác tử.
6. **Kiểm tra mục tiêu (Goal Test):** Hàm kiểm tra xem một trạng thái có phải là trạng thái đích/mục tiêu hay không.

---

### 6 Thành phần cấu thành Bài toán Tìm kiếm cho Pipes (FreeNet)

* **Trạng thái bắt đầu (Start State):** Cấu hình khởi đầu của bảng lưới kích thước $N \times M$, trong đó mỗi ô chứa một đoạn ống (thẳng, góc, nhánh T, chữ thập, hoặc mút nối) với các hướng xoay ban đầu ngẫu nhiên.
* **Không gian trạng thái (State Space):** Tập hợp tất cả các cấu hình có thể có của toàn bộ bàn cờ. Nếu bảng lưới có $K = N \times M$ ô và mỗi ô có tối đa 4 hướng xoay ($0^\circ, 90^\circ, 180^\circ, 270^\circ$), kích thước không gian trạng thái tối đa sẽ là $4^{N \times M}$ trạng thái.
* **Tập hợp các hành động (Actions):** Tại mỗi trạng thái, hành động khả thi là chọn một ô cụ thể tại vị trí $(i, j)$ và xoay ô đó $90^\circ$ theo chiều kim đồng hồ (hoặc ngược chiều kim đồng hồ).
* **Mô hình chuyển trạng thái (Transition Model):** Hàm nhận vào trạng thái hiện tại và một hành động xoay ô $(i, j)$, trả về trạng thái bàn cờ mới trong đó góc xoay của ô $(i, j)$ đã thay đổi, còn tất cả các ô khác giữ nguyên vị trí và góc xoay.
* **Chi phí hành động (Action Cost):** Mỗi lần xoay một ô thường được tính chi phí đồng nhất là 1 ($\text{cost} = 1$). Việc gán chi phí này giúp thuật toán tìm kiếm hướng tới lời giải có tổng số lượt xoay là ít nhất.
* **Kiểm tra mục tiêu (Goal Test):** Hàm logic kiểm tra xem trạng thái bàn cờ hiện tại có thỏa mãn đồng thời hai quy tắc thắng cuộc của Pipes hay không: 
  1. **Tính liên thông hoàn toàn:** Tất cả các đoạn ống trên bàn cờ đều được kết nối với nhau thành một mạng lưới duy nhất (*single connected group*).
  2. **Không có vòng kín & không có đầu hở:** Bàn cờ không chứa bất kỳ vòng kín nào (*no closed loops*) và không có đầu ống nào chĩa vào ô trống hoặc bức tường ngoài biên.

---

### Xây dựng Cây Tìm Kiếm cho Pipes

Để xây dựng một Cây tìm kiếm (Search Tree) cho trò chơi Pipes (FreeNet), thuật toán AI không dựng sẵn toàn bộ cây vào bộ nhớ (vì kích thước không gian trạng thái lên tới $4^{N \times M}$ trạng thái). Thay vào đó, cây tìm kiếm được sinh ra một cách linh hoạt theo nhu cầu (*on-demand*) trong quá trình duyệt không gian trạng thái.

Cấu trúc một **Nút (Node)** trong cây tìm kiếm cho Pipes không chỉ lưu trạng thái bàn cờ ($S$), mà còn lưu giữ:
* `State`: Cấu hình xoay hiện tại của các ô ống trên bàn cờ.
* `Parent`: Con trỏ trỏ về nút cha đã sinh ra nút này.
* `Action`: Hành động xoay ô $(i, j)$ thêm $90^\circ$ dẫn đến trạng thái này.
* `PathCost`: Tổng chi phí bước đi (tổng số lần xoay từ bàn cờ ban đầu).

#### Quy trình 5 bước chi tiết:

1. **Bước 1: Khởi tạo Nút gốc (Make Root Node)**
   * Tạo Nút gốc (Root node) đại diện cho trạng thái ban đầu của bàn cờ Pipes (với các góc xoay ngẫu nhiên ban đầu).
   * Gán các thuộc tính: $\text{Parent} = \text{null}$, $\text{Action} = \text{null}$, $\text{PathCost} = 0$.
   * Đưa Nút gốc này vào Frontier (Tập các nút biên đang chờ xét).

2. **Bước 2: Kiểm tra tập Frontier (Frontier Check)**
   * Kiểm tra xem tập Frontier có rỗng hay không: 
     * Nếu Frontier rỗng: Thuật toán dừng lại và thông báo **Thất bại** (không tìm được lời giải nối ống).
     * Nếu Frontier không rỗng: Lấy ra một nút $N$ từ Frontier dựa trên chiến lược tìm kiếm được lựa chọn (ví dụ: DFS chọn nút sâu nhất, BFS chọn nút nông nhất, UCS/A* chọn nút có chi phí tối ưu nhất).

3. **Bước 3: Kiểm tra mục tiêu (Goal Test)**
   * Kiểm tra trạng thái bàn cờ $N.\text{State}$ có thỏa mãn điều kiện thắng của game Pipes hay không: 
     * *Điều kiện Goal:* Tất cả các đường ống nối liền thành một mạng duy nhất, không có vòng kín và không có đầu ống bị hở.
     * Nếu đạt Goal: Thuật toán dừng và truy vết ngược từ $N$ về Nút gốc thông qua con trỏ `Parent` để xuất ra chuỗi danh sách các ô cần xoay (kế hoạch giải đố / Plan).
     * Nếu chưa đạt Goal: Chuyển sang Bước 4.

4. **Bước 4: Mở rộng nút (Node Expansion)**
   * Gọi hàm `EXPAND(problem, N)` để sinh tất cả các nút con khả thi từ nút $N$: 
     * Xác định các hành động: Duyệt qua các ô lưới và tạo ra các hành động xoay $90^\circ$ (theo chiều kim đồng hồ hoặc ngược chiều).
     * Áp dụng mô hình chuyển trạng thái: Tạo ra cấu hình bàn cờ mới $S'$ sau khi xoay ô tương ứng.
     * Tạo các nút con mới ($N_{\text{child}}$): 
       * $N_{\text{child}}.\text{State} = S'$
       * $N_{\text{child}}.\text{Parent} = N$
       * $N_{\text{child}}.\text{Action} = \text{xoay ô } (i, j) \text{ góc } 90^\circ$
       * $N_{\text{child}}.\text{PathCost} = N.\text{PathCost} + 1$

5. **Bước 5: Cập nhật Frontier & Tránh lặp trạng thái (Graph Search)**
   * Thêm các nút con mới sinh ra vào Frontier.
   * **Cơ chế Graph Search (Loại bỏ chu trình):** Để tránh việc lặp vô tận (ví dụ: xoay ô $(0, 0)$ 4 lần liên tiếp đưa bàn cờ trở về trạng thái cũ), ta duy trì một tập hợp các trạng thái đã mở rộng (*Reached set / Explored set*). Nếu một trạng thái $S'$ sinh ra đã xuất hiện trong Reached với chi phí bằng hoặc rẻ hơn, ta sẽ loại bỏ (*prune*) nút con đó.
   * Lặp lại Bước 2 cho đến khi tìm ra lời giải.

---

### 6 Thành phần cấu thành Bài toán Tìm kiếm cho Hashi (Bridges)

1. **Trạng thái bắt đầu (Start State):**
   * Cấu hình ban đầu của lưới $N \times M$ chứa vị trí cố định của các hòn đảo và con số yêu cầu (từ 1 đến 8) ghi trên từng đảo. Tại thời điểm xuất phát, chưa có cây cầu nào được đặt .

2. **Không gian trạng thái (State Space):**
   * Tập hợp tất cả các cấu hình phân bố cầu khả thi trên bàn cờ. 
   * Mỗi trạng thái đại diện cho một cách gán số lượng cầu (0, 1 hoặc 2) cho các đường nối tiềm năng theo chiều ngang/dọc giữa các cặp hòn đảo lân cận.

3. **Tập hợp các hành động (Actions):**
   * Tại một trạng thái, hành động khả thi là chọn hai hòn đảo $I_a$ và $I_b$ (nằm trên cùng hàng hoặc cùng cột, không bị đảo khác chắn) và **đặt thêm 1 cây cầu đơn (hoặc nâng cấp thành cầu đôi)** giữa hai đảo đó.
   * Điều kiện hành động hợp lệ: Cầu mới không được cắt ngang qua bất kỳ cây cầu nào đã có và số lượng cầu giữa $I_a, I_b$ sau khi đặt không vượt quá 2.

4. **Mô hình chuyển trạng thái (Transition Model):**
   * Hàm nhận vào trạng thái bàn cờ hiện tại $S$ và hành động đặt/thay đổi cầu giữa hai đảo $I_a, I_b$.
   * Trả về **trạng thái bàn cờ mới $S'$**, trong đó số lượng cầu giữa $I_a$ và $I_b$ tăng lên (0 → 1 hoặc 1 → 2), trong khi toàn bộ các cầu khác trên bàn cờ giữ nguyên.

5. **Chi phí hành động (Action Cost):**
   * Mỗi lần thực hiện thao tác xây một cây cầu được tính chi phí đồng nhất là **1** (cost = 1). 
   * Tổng chi phí đường đi chính là tổng số cầu được đặt để đi từ bàn cờ trống ban đầu đến lời giải hoàn chỉnh.

6. **Kiểm tra mục tiêu (Goal Test):**
   * Hàm logic kiểm tra xem trạng thái bàn cờ hiện tại có thỏa mãn đồng thời tất cả các điều kiện thắng của Hashi hay không:
     * **Đúng số lượng cầu:** Tổng số cầu nối vào mỗi hòn đảo đúng bằng con số ghi trên hòn đảo đó.
     * **Tính liên thông hoàn toàn:** Tất cả các hòn đảo được kết nối với nhau thành **một nhóm/đồ thị liên thông duy nhất** (không có đảo hay cụm đảo nào bị cô lập).
     * **Tuân thủ quy tắc hình học:** Cầu chỉ chạy theo chiều ngang hoặc chiều dọc, không có hai cầu nào cắt nhau và không quá 2 cầu nối giữa một cặp đảo.

---

Tương tự như game Pipes, để giải trò chơi **Hashi (Bridges)** bằng thuật toán AI, cây tìm kiếm (**Search Tree**) được sinh ra một cách linh hoạt (**on-demand**) theo nhu cầu khám phá thay vì dựng sẵn toàn bộ vào bộ nhớ.

Mỗi **Nút (Node)** trong Cây tìm kiếm của Hashi lưu giữ các thông tin sau:
* `State`: Cấu hình hiện tại của bàn cờ (vị trí các cây cầu đã được đặt giữa các cặp đảo).
* `Parent`: Con trỏ trỏ về nút cha đã sinh ra nút này.
* `Action`: Hành động đặt cầu (thêm 1 cầu đơn hoặc nâng cấp thành cầu đôi) giữa hai hòn đảo $(I_a, I_b)$.
* `PathCost`: Tổng số cầu đã được đặt từ trạng thái bàn cờ ban đầu.

---

### Xây dựng Cây tìm kiếm cho Hashi

#### Bước 1: Khởi tạo Nút gốc (Make Root Node)
* Tạo **Nút gốc (Root node)** đại diện cho trạng thái ban đầu của bàn cờ Hashi (chứa vị trí các hòn đảo và số lượng cầu mục tiêu, nhưng **chưa có cây cầu nào được đặt**).
* Gán các thuộc tính: $\text{Parent} = \text{null}$, $\text{Action} = \text{null}$, $\text{PathCost} = 0$.
* Đưa Nút gốc này vào tập biên **Frontier** (hàng chờ các nút chuẩn bị xét).

#### Bước 2: Kiểm tra tập Frontier (Frontier Check)
* Kiểm tra xem tập Frontier có rỗng hay không:
  * **Nếu Frontier rỗng:** Dừng thuật toán và thông báo **Thất bại** (cấu hình câu đố không có lời giải).
  * **Nếu Frontier không rỗng:** Lấy ra một nút $N$ từ Frontier theo chiến lược tìm kiếm (ví dụ: DFS lấy nút sâu nhất, BFS lấy nút nông nhất, A* lấy nút có hàm đánh giá tốt nhất).

#### Bước 3: Kiểm tra mục tiêu (Goal Test)
* Kiểm tra trạng thái bàn cờ $N.\text{State}$ có thỏa mãn tất cả điều kiện thắng của game Hashi hay không:
  1. **Đúng số lượng cầu:** Số cầu nối vào mỗi đảo đúng bằng con số ghi trên đảo đó.
  2. **Tính liên thông hoàn toàn:** Tất cả các đảo nối liền thành **một đồ thị liên thông duy nhất** (không có đảo hay cụm đảo cô lập).
  3. **Quy tắc hình học:** Không có cầu cắt nhau, không quá 2 cầu giữa 2 đảo.
* **Nếu đạt Goal:** Thuật toán dừng và **truy vết ngược (backtrack)** từ $N$ về Nút gốc qua con trỏ `Parent` để xuất ra thứ tự các cây cầu cần đặt (Kế hoạch / **Plan**).
* **Nếu chưa đạt Goal:** Chuyển sang Bước 4.

#### Bước 4: Mở rộng nút (Node Expansion)
* Gọi hàm `EXPAND(problem, N)` để sinh tất cả các nút con khả thi từ nút $N$:
  1. **Xác định đường nối hợp lệ:** Tìm tất cả các cặp đảo $(I_a, I_b)$ nằm trên cùng hàng hoặc cùng cột mà đường nối giữa chúng chưa bị chặn bởi đảo hoặc cây cầu khác, và số cầu hiện tại giữa chúng chưa vượt quá 2.
  2. **Tạo hành động:** Sinh hành động đặt 1 cầu đơn hoặc nâng cấp lên cầu đôi giữa $I_a$ và $I_b$.
  3. **Tạo các nút con mới ($N_{\text{child}}$):**
     * $N_{\text{child}}.\text{State} = \text{Trạng thái bàn cờ mới sau khi đặt cầu}$
     * $N_{\text{child}}.\text{Parent} = N$
     * $N_{\text{child}}.\text{Action} = \text{đặt/thêm cầu giữa } (I_a, I_b)$
     * $N_{\text{child}}.\text{PathCost} = N.\text{PathCost} + 1$.

#### Bước 5: Cập nhật Frontier & Tránh lặp trạng thái (Graph Search)
* Đưa các nút con mới sinh ra vào **Frontier**.
* **Cơ chế Graph Search:** Duy trì một tập hợp các trạng thái bàn cờ đã duyệt (**Reached / Explored set**). Nếu một cấu hình phân bố cầu đã từng được duyệt trước đó, ta sẽ bỏ qua (prune) nút con trùng lặp để tránh việc vòng lặp vô tận (ví dụ: đặt cầu rồi xóa cầu lặp đi lặp lại).
* Lặp lại **Bước 2** cho đến khi tìm thấy lời giải.

---

## 1.3 Uninformed Search


### 1. Khung thuật toán tổng quát (Tree Search) & 4 Tiêu chí đánh giá

Mọi thuật toán Uninformed Search đều hoạt động dựa trên nguyên lý duy trì một tập biên (**Frontier**) lưu giữ các kế hoạch một phần xuất phát từ nút gốc. Thuật toán liên tục lấy một nút ra khỏi Frontier dựa theo một chiến lược cụ thể, kiểm tra xem nút đó có phải mục tiêu không, và mở rộng (**Expand**) các nút con của nó vào Frontier.

Để so sánh và đánh giá các chiến lược tìm kiếm, ta dùng **4 tiêu chí chuẩn**:
* **Completeness (Tính đầy đủ):** Thuật toán có đảm bảo tìm thấy lời giải hay không (nếu lời giải tồn tại)?
* **Optimality (Tính tối ưu):** Thuật toán có đảm bảo tìm ra đường đi có tổng chi phí nhỏ nhất hay không?
* **Time Complexity (Độ phức tạp thời gian):** Số lượng nút cần kiểm tra/mở rộng.
* **Space Complexity (Độ phức tạp không gian):** Số lượng nút tối đa phải lưu giữ trong bộ nhớ (Frontier) tại một thời điểm.

*(Trong đó: $b$ là hệ số nhánh - số nút con trung bình của một nút; $m$ là độ sâu tối đa của cây tìm kiếm; $s$ là độ sâu của lời giải nông nhất).*

---

### 2. Ba thuật toán Uninformed Search cốt lõi

#### 🟢 2.1 Depth-First Search (DFS) - Tìm kiếm theo chiều sâu
* **Mô tả:** Luôn chọn mở rộng nút **sâu nhất** hiện có trên Frontier.
* **Cấu trúc Frontier:** **LIFO Stack (Ngăn xếp)** — nút mới sinh ra sẽ có độ sâu lớn hơn và được ưu tiên duyệt ngay lập tức.
* **Completeness:** **Không đầy đủ**. Trong các không gian trạng thái có chu trình (cycles) hoặc độ sâu vô hạn, DFS có thể bị kẹt vĩnh viễn ở nhánh sâu mà không bao giờ tìm ra lời giải ở các nhánh khác.
* **Optimality:** **Không tối ưu**. DFS chỉ trả về lời giải đầu tiên mà nó chạm tới ở nhánh trái ngoài cùng.
* **Độ phức tạp thời gian:** $O(b^m)$ ở trường hợp xấu nhất.
* **Độ phức tạp không gian:** **$O(bm)$**. Đây là ưu điểm lớn nhất của DFS vì bộ nhớ chỉ cần lưu các nút con tại từng tầng trên nhánh đang duyệt.

#### 🔵 2.2 Breadth-First Search (BFS) - Tìm kiếm theo chiều rộng
* **Mô tả:** Luôn chọn mở rộng nút **nông nhất** (gần gốc nhất) trên Frontier.
* **Cấu trúc Frontier:** **FIFO Queue (Hàng đợi)** — nút nào vào trước sẽ được duyệt trước.
* **Completeness:** **Đầy đủ**. Nếu lời giải tồn tại ở độ sâu $s$ hữu hạn, BFS chắc chắn sẽ tìm ra.
* **Optimality:** **Chỉ tối ưu khi chi phí mọi hành động là như nhau** (ví dụ: mỗi bước di chuyển đều tốn 1 chi phí). Nếu chi phí các cạnh không bằng nhau, BFS không đảm bảo tính tối ưu.
* **Độ phức tạp thời gian:** $O(b^s)$.
* **Độ phức tạp không gian:** **$O(b^s)$**. BFS đòi hỏi dung lượng bộ nhớ rất lớn vì phải lưu lại toàn bộ các nút ở tầng $s$.

#### 🟡 2.3 Uniform Cost Search (UCS) - Tìm kiếm chi phí đồng nhất
* **Mô tả:** Mở rộng nút có **chi phí đường đi tích lũy $g(n)$ nhỏ nhất** từ trạng thái bắt đầu.
* **Cấu trúc Frontier:** **Priority Queue (Hàng đợi ưu tiên)** sắp xếp theo chi phí $g(n)$.
* **Completeness & Optimality:** **Đầy đủ và Tối ưu** với điều kiện chi phí mỗi bước đi đều là số dương ($\ge \epsilon > 0$). Nguyên lý của UCS hoàn toàn tương tự thuật toán Dijkstra, nhưng UCS dừng lại ngay khi lấy được trạng thái mục tiêu ra khỏi Frontier.
* **Độ phức tạp thời gian & không gian:** $O(b^{C^* / \epsilon})$, trong đó $C^*$ là chi phí của đường đi tối ưu và $\epsilon$ is chi phí nhỏ nhất giữa 2 trạng thái.

---

### 3. Tóm tắt so sánh giữa DFS, BFS và UCS

| Thuật toán | Chiến lược mở rộng nút | Cấu trúc Frontier | Tính đầy đủ | Tính tối ưu | Độ phức tạp thời gian | Độ phức tạp không gian |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DFS** | Nút sâu nhất | LIFO Stack | ❌ Không | ❌ Không | $O(b^m)$ | **$O(bm)$** (Tiết kiệm) |
| **BFS** | Nút nông nhất | FIFO Queue | ✅ Có | ⚠️ Chỉ khi chi phí bằng nhau | $O(b^s)$ | $O(b^s)$ (Tốn RAM) |
| **UCS** | Chi phí $g(n)$ nhỏ nhất | Priority Queue | ✅ Có | ✅ Có | $O(b^{C^* / \epsilon})$ | $O(b^{C^* / \epsilon})$ |

---

💡 **Trong bài toán Pacman hay Pipes/Hashi, nếu ta có thêm thông tin định hướng (ví dụ: khoảng cách Manhattan tới điểm đích), ta có thể chuyển sang Informed Search (1.4 A* Search & Heuristic) để tìm lời giải nhanh hơn nhiều. Bạn có muốn chuyển sang mục 1.4 Informed Search không?**

---

## 1.4 Informed Search

### 1. Khái niệm Hàm Heuristic $h(n)$
* **Định nghĩa:** Hàm Heuristic $h(n)$ nhận vào một trạng thái $n$ và trả về một **ước lượng chi phí còn lại (forward cost)** từ $n$ đến trạng thái đích.
* **Giải bài toán nới lỏng (Relaxed Problems):** Hàm heuristic thường được xây dựng bằng cách giải một bài toán nới lỏng — bài toán đã bỏ bớt một số ràng buộc của bài toán gốc.
  * *Ví dụ (Pacman Pathing):* Khoảng cách Manhattan $\text{Manhattan}(x_1, y_1, x_2, y_2) = |x_1 - x_2| + |y_1 - y_2|$ là khoảng cách chính xác để Pacman đi đến đích trong bài toán đã được nới lỏng bỏ đi các bức tường trong mê cung.

---

### 2. Hai thuật toán Informed Search cốt lõi

#### 🟡 2.1 Greedy Best-First Search (Tìm kiếm tham ăn)
* **Chiến lược:** Luôn chọn mở rộng nút trên Frontier có **giá trị heuristic $h(n)$ nhỏ nhất** (nút mà nó tin là gần đích nhất).
* **Cấu trúc Frontier:** Priority Queue sắp xếp theo ưu tiên $h(n)$.
* **Đánh giá:** **Không đầy đủ và Không tối ưu**. Nếu dùng một hàm $h(n)$ không tốt, thuật toán có thể rơi vào đường vòng hoặc bị dẫn dắt sang các nhánh sai lầm giống như DFS.

#### 🟢 2.2 A* Search (Tìm kiếm A*)
* **Chiến lược:** Kết hợp chi phí tích lũy quá khứ $g(n)$ (từ UCS) và ước lượng chi phí tương lai $h(n)$ (từ Greedy Search).
* **Công thức hàm đánh giá:**
  \\[f(n) = g(n) + h(n)\\]
  * $g(n)$: Chi phí thực tế tích lũy từ trạng thái bắt đầu đến nút $n$.
  * $h(n)$: Chi phí ước lượng từ nút $n$ đến mục tiêu.
  * $f(n)$: Chi phí tổng ước lượng của cả đường đi từ điểm đầu qua $n$ đến mục tiêu.
* **Cấu trúc Frontier:** Priority Queue sắp xếp theo giá trị $f(n)$ nhỏ nhất.
* **Đánh giá:** **Đầy đủ và Tối ưu** (khi chọn hàm Heuristic thỏa mãn điều kiện thích hợp). A* kết hợp tốc độ của Greedy Search với tính tối ưu của UCS.

---

### 3. Điều kiện Tối ưu cho A*: Tính Chấp nhận được (Admissibility)

Một hàm heuristic $h(n)$ được gọi là **Admissible (Chấp nhận được)** nếu nó không âm và **không bao giờ đánh giá cao hơn chi phí thực tế** $h^*(n)$ để tới đích:
\\[0 \le h(n) \le h^*(n), \quad \forall n\\]
* Với mọi trạng thái mục tiêu $G$, ta luôn có $h(G) = 0$.
* **Định lý:** Đối với A* Tree Search, nếu $h(n)$ thỏa mãn tính Admissibility, thuật toán A* chắc chắn tìm ra lời giải tối ưu.
* **Lưu ý với Graph Search:** Trong A* Graph Search, để duy trì tính tối ưu khi sử dụng tập trạng thái đã duyệt (`reached`), nếu gặp lại một trạng thái đã có trong `reached`, ta phải kiểm tra xem đường đi mới có chi phí rẻ hơn không để cập nhật lại.

---

### 4. So sánh & Kết hợp Heuristic (Dominance)

* **Tính trội (Dominance):** Một heuristic $h_a$ được gọi là **trội hơn** $h_b$ nếu $h_a(n) \ge h_b(n)$ với mọi nút $n$. Heuristic trội hơn sẽ đưa ra ước lượng sát với chi phí thực tế hơn, giúp A* mở rộng ít nút hơn.
* **Heuristic tầm thường (Trivial Heuristic):** Chọn $h(n) = 0$ làm A* biến thành thuật toán UCS.
* **Kết hợp nhiều Heuristic:** Nếu có nhiều heuristic chấp nhận được $h_a, h_b$, ta có thể tạo hàm heuristic mới $h(n) = \max(h_a(n), h_b(n))$. Hàm này chắc chắn vừa chấp nhận được vừa trội hơn cả $h_a$ lẫn $h_b$.

---

### 💡 Để áp dụng thuật toán **Informed Search (Tìm kiếm có thông tin)** — cụ thể là **A* Search** hoặc **Greedy Best-First Search** — cho game **Pipes (FreeNet)**, chìa khóa quan trọng nhất là việc thiết kế một **Hàm Heuristic $h(n)$** thông minh.

Thay vì duyệt tất cả các hướng xoay một cách mù mờ như BFS hay DFS, Informed Search sử dụng hàm đánh giá $f(n)$ để ưu tiên mở rộng các cấu hình bàn cờ có tiềm năng hoàn thành cao nhất.

---

### 1. Hàm đánh giá trong A* Search cho Pipes

Đối với thuật toán A*, mỗi trạng thái bàn cờ $n$ được gán một giá trị ưu tiên:

$$f(n) = g(n) + h(n)$$

* **$g(n)$:** Chi phí thực tế tích lũy từ bàn cờ ban đầu đến trạng thái $n$ (tổng số lượt xoay các ô đã thực hiện).
* **$h(n)$:** Ước lượng số lượt xoay **còn lại** từ bàn cờ hiện tại đến khi hoàn thành toàn bộ mạng lưới.

---

### 2. Thiết kế các Hàm Heuristic $h(n)$ cho Pipes

Hàm Heuristic thường được xây dựng dựa trên việc **giải bài toán nới lỏng (Relaxed Problem)** — bỏ qua một số ràng buộc phức tạp để tính toán nhanh khoảng cách tới mục tiêu. Với game Pipes, ta có thể xây dựng các heuristic sau:

#### 💡 Heuristic 1: Số lượng ô chứa đầu ống chưa khớp (Mismatched Connections)
* **Cách tính:** Đếm tổng số ô có ít nhất 1 đầu ống chĩa vào bức tường ngoài biên hoặc chĩa vào ô lân cận mà ô đó không có đầu ống đối ứng (đầu hở).
* **Công thức ước lượng:** 

$h_1(n) = \lceil \text{Tổng số đầu hở} / 2 \rceil$ (hoặc đơn giản là số lượng ô chưa được khớp nối chính xác).

$h^*(n)$ là con số hoàn hảo để đến đích
* **Tính chấp nhận được (Admissibility):** Vì mỗi lượt xoay chỉ có thể sửa góc cho 1 ô duy nhất, số bước xoay tối thiểu cần thiết để sửa tất cả các ô sai hướng chắc chắn không nhỏ hơn số ô đang bị lỗi. Do đó $0 \le h_1(n) \le h^*(n)$, đảm bảo A* luôn tìm ra lời giải tối ưu.

#### 💡 Heuristic 2: Số lượng thành phần liên thông (Number of Disconnected Components)
* **Cách tính:** Trong Pipes, quy tắc thắng cuộc bắt buộc tất cả các đoạn ống phải nối liền thành **1 cụm duy nhất**.
* **Công thức ước lượng:** $h_2(n) = \text{Số cụm mạng lưới rời rạc hiện tại} - 1$.
* **Ý nghĩa:** Nếu các đoạn ống đang bị phân mảnh thành 5 cụm độc lập, agent cần ít nhất 4 thao tác nối/xoay hợp lệ để gộp chúng lại thành 1 mạng duy nhất.

#### 💡 Heuristic 3: Kết hợp các Heuristic (Dominance)
* Để tạo ra một heuristic mạnh hơn nữa, ta lấy giá trị lớn nhất giữa các heuristic chấp nhận được:
  $$h(n) = \max(h_1(n), h_2(n))$$
* Hàm $h(n)$ này vừa **Admissible** (không đánh giá cao hơn thực tế) vừa **Dominant** (cho ước lượng sát với chi phí thực hơn), giúp A* loại bỏ bớt hàng loạt nút không triển vọng trên cây tìm kiếm.


---

### 3. Quy trình thực thi A* Search trên Game Pipes

1. **Khởi tạo Frontier:** Đưa bàn cờ ban đầu vào **Priority Queue**, sắp xếp ưu tiên theo giá trị $f(n) = g(n) + h(n)$ nhỏ nhất.
2. **Chọn nút mở rộng:** Lấy bàn cờ có $f(n)$ nhỏ nhất ra khỏi Frontier.
3. **Mở rộng (Expand):** Sinh ra các trạng thái con bằng cách thử xoay từng ô chưa cố định $90^\circ$.
   * Chi phí mới: $g(\text{con}) = g(\text{cha}) + 1$.
   * Tính lại $h(\text{con})$ dựa trên số đầu hở còn lại.
4. **Graph Search (Loại bỏ lặp):** Lưu các cấu hình bàn cờ đã duyệt vào tập `reached` cùng giá trị $g$ nhỏ nhất để tránh việc lặp lại thao tác xoay vòng.
5. **Kiểm tra Goal:** Khi nút lấy ra khỏi Frontier có $h(n) = 0$ (tất cả các ống nối liền thành 1 cụm, không có đầu hở hay vòng kín), A* dừng lại và trả về chuỗi các ô cần xoay.

---

### 4. Hiệu quả so với Uninformed Search

* Với **BFS / DFS**, việc duyệt một không gian trạng thái lên tới $4^{N \times M}$ làm thuật toán nhanh chóng bị bùng nổ bộ nhớ hoặc chìm vào các nhánh vô vọng.
* Với **A* Search**, nhờ có thông tin định hướng từ hàm $h(n)$ ("bàn cờ nào càng ít đầu hở thì càng được ưu tiên duyệt trước"), thuật toán sẽ **bỏ qua hầu hết các nhánh xoay sai** và đi thẳng tới cấu hình bàn cờ hoàn chỉnh.

---

🧩 Bạn chỉ nên chọn **Local Search** (cụ thể là thuật toán **Min-Conflicts** hoặc **Simulated Annealing**) trên các bàn cờ kích thước siêu lớn (ví dụ $15 \times 15$ trở lên).**

---

### 💡 Để áp dụng thuật toán **Informed Search (Tìm kiếm có thông tin)** — tiêu biểu là **A\* Search** hoặc **Greedy Best-First Search** — cho trò chơi **Hashi (Bridges)**, chìa khóa cốt lõi nằm ở việc thiết kế **Hàm Heuristic $h(n)$** dựa trên các quy tắc nối đảo của game.
---



### 1. Hàm đánh giá trong A* Search cho Hashi

Trong thuật toán A*, mỗi trạng thái bàn cờ Hashi $n$ được gán một giá trị ưu tiên:

$$f(n) = g(n) + h(n)$$

* **$g(n)$:** Chi phí thực tế tích lũy từ trạng thái bắt đầu (tổng số cây cầu đã được đặt trên bàn cờ tính đến thời điểm hiện tại).
* **$h(n)$:** Ước lượng chi phí (số cây cầu) **còn phải đặt thêm** từ trạng thái $n$ để hoàn thành toàn bộ bàn cờ.

---

### 2. Thiết kế các Hàm Heuristic $h(n)$ cho Hashi (Dựa trên Relaxed Problems)

Hàm Heuristic được xây dựng bằng cách giải một **bài toán nới lỏng (Relaxed Problem)** — tạm thời bỏ qua một số quy tắc hình học phức tạp để tính toán nhanh khoảng cách tới mục tiêu:

#### 💡 Heuristic 1: Tổng số cầu còn thiếu trên các đảo (Bridge Deficit Heuristic)
* **Quy tắc Hashi:** Mỗi hòn đảo $i$ ghi một con số mục tiêu $N_i$, và hiện tại đang có $d_i$ cây cầu nối vào nó.
* **Cách tính:** Số cầu còn thiếu của đảo $i$ là $\max(0, N_i - d_i)$.
* Vì mỗi cây cầu khi được đặt giữa hai hòn đảo sẽ đóng góp 1 cầu cho mỗi đầu đảo (giúp làm giảm tổng độ thiếu hụt của cả bàn cờ tối đa 2 đơn vị):
  $$h_1(n) = \left\lceil \frac{\sum_i \max(0, N_i - d_i)}{2} \right\rceil$$
* **Tính chấp nhận được (Admissible):** Do mỗi bước đặt 1 cây cầu chỉ có thể giảm tối đa 2 đơn vị thiếu hụt trên toàn bản đồ, số lượng cầu thực tế $h^*(n)$ cần đặt chắc chắn không thể nhỏ hơn $h_1(n)$. Vì $0 \le h_1(n) \le h^*(n)$, hàm $h_1(n)$ thỏa mãn điều kiện **Admissibility**, đảm bảo A* luôn tìm ra lời giải tối ưu.

#### 💡 Heuristic 2: Số lượng thành phần liên thông (Disconnected Components Heuristic)
* **Quy tắc Hashi:** Tất cả các hòn đảo phải được kết nối với nhau thành **một đồ thị/nhóm liên thông duy nhất**.
* **Cách tính:** Nếu các cây cầu hiện tại đang chia bàn cờ thành $K$ cụm đảo độc lập, agent cần ít nhất $K - 1$ cây cầu nữa để nối tất cả các cụm này lại với nhau.
  $$h_2(n) = K - 1$$
* **Tính chấp nhận được (Admissible):** Để hợp nhất $K$ thành phần rời rạc thành 1 nhóm duy nhất, số cạnh (cầu) tối thiểu cần thêm vào luôn là $K - 1$.


#### 💡 Heuristic 3: Nút thắt cổ chai và giới hạn hướng đi (`bottleneck_corrected`)

* **Quy tắc Hashi:** Mỗi hòn đảo bị giới hạn bởi không gian vật lý xung quanh, chỉ có thể vươn ra một số hướng đi khả dụng nhất định.
* **Cách tính:**
  * Xét nhu cầu cầu còn thiếu của hòn đảo ($d$). 
  * Đếm số lượng hướng đi/hành lang lân cận còn khả dụng (`available_edges`).
  * Nếu nhu cầu của đảo vượt quá số hướng đi khả dụng ($d > \text{available\_edges}$), phần chênh lệch $\max(0, d - \text{available\_edges})$ chính là điểm nghẽn bắt buộc phải xây dựng cầu đôi (double bridges).


* **Công thức ước lượng:**

$$h_3(n) = \left\lceil \frac{1}{2} \sum_{i} \max\left(0, \text{demand}_i - \text{available\_edges}_i\right) \right\rceil$$


* **Ý nghĩa:** Giúp A* nhận diện trước các điểm nghẽn vật lý khắt khe trên lưới mà chỉ đếm số cầu thiếu đơn thuần không phản ánh hết.

#### 💡 Heuristic 4: Kết hợp Heuristic cực đại (Dominant Heuristic)

* Để tạo ra hàm heuristic mạnh nhất, ta lấy giá trị cực đại giữa tất cả các hàm heuristic chấp nhận được:

$$h(n) = \max\Big(h_1(n), h_2(n), h_3(n)\Big)$$


* Hàm $h(n)$ này vừa **Admissible** vừa **Dominant** (trội hơn các hàm thành phần), giúp thuật toán A* ước lượng sát chi phí thực tế hơn, nhận diện sớm các thế cục hiểm nghèo và loại bỏ bớt nhiều nhánh tìm kiếm không cần thiết.
---

### 3. Kỹ thuật Cắt tỉa trạng thái chết (Deadlock Pruning)

Trò chơi Hashi có đặc thù là một bước đặt cầu sai có thể làm "chết" các hòn đảo xung quanh. Do đó, ta áp dụng kỹ thuật cắt tỉa sớm:
* **Phát hiện trạng thái vi phạm:** Nếu một hành động đặt cầu khiến tổng số cầu của một đảo vượt quá con số yêu cầu ($d_i > N_i$), hoặc làm hai cây cầu cắt nhau, hoặc tạo ra một cụm đảo cô lập đã đủ cầu nhưng chưa nối với phần còn lại của bàn cờ, trạng thái đó là không hợp lệ.
* **Gán chi phí vô cùng:** Ta gán $h(n) = \infty$ cho các trạng thái này để A* loại bỏ ngay lập tức khỏi Frontier.

---

### 4. Quy trình thực thi A* Search trên Game Hashi

1. **Khởi tạo Frontier:** Đưa bàn cờ ban đầu (chưa có cây cầu nào) vào **Priority Queue**, sắp xếp ưu tiên theo giá trị $f(n) = g(n) + h(n)$ nhỏ nhất.
2. **Chọn nút mở rộng:** Lấy trạng thái bàn cờ có $f(n)$ nhỏ nhất ra khỏi Frontier.
3. **Mở rộng (Expand):** Tìm các cặp đảo kề nhau theo chiều ngang/dọc chưa bị chặn và sinh các trạng thái con bằng cách đặt 1 cầu đơn hoặc cầu đôi.
4. **Graph Search Optimization:** Duy trì tập `reached` để lưu các cấu hình phân bố cầu đã duyệt cùng chi phí $g(n)$ nhỏ nhất, tránh việc lặp lại các chu trình thử-xóa cầu.
5. **Kiểm tra Goal:** Thuật toán dừng khi lấy ra trạng thái có $h(n) = 0$ (mọi hòn đảo đều đạt đúng số cầu yêu cầu và toàn bộ bàn cờ liên thông hoàn toàn).

---

### 5. So sánh hiệu quả với Uninformed Search

* **DFS / BFS:** Dễ rơi vào tình trạng bùng nổ tổ hợp do số lượng cặp đảo có thể nối là rất lớn, dẫn tới việc tìm kiếm vô hướng và dễ bị nghẽn bộ nhớ.
* **A\* Search:** Nhờ hàm $h(n)$ định hướng ("bàn cờ nào còn ít thiếu hụt cầu và ít bị phân mảnh cụm nhất sẽ được ưu tiên duyệt trước"), A* sẽ tập trung thẳng vào các nước đi chính xác và hoàn thành câu đố nhanh hơn đáng kể.

---

🧩 **Game Hashi và Pipes cũng là hai ví dụ rất kinh điển để chuyển đổi sang Bài toán Thỏa mãn Ràng buộc (CSP) ở Chương 2. Bạn có muốn xem thử cách giải Hashi bằng thuật toán Backtracking Search kết hợp kiểm tra Arc Consistency (AC-3) không?**

---

## 1.5 Local Search 

### 1. Tổng quan về Tìm kiếm Cục bộ (Local Search)

* **Sự khác biệt cốt lõi:** Trong các bài toán tìm kiếm lập kế hoạch, tác tử cần tìm một chuỗi hành động (đường đi / plan) từ trạng thái đầu đến đích. Tuy nhiên, đối với nhiều bài toán thực tế (như Sudoku, xếp lịch hay bài toán 8-Queens), chúng ta chỉ quan tâm đến **trạng thái đích / cấu hình tối ưu** thỏa mãn các ràng buộc mà không cần quan tâm đến cách thức di chuyển để tới đó.
* **Cơ chế hoạt động:** Local Search duyệt trên không gian các lời giải "hoàn chỉnh" (complete solutions). Thay vì duy trì cây tìm kiếm (search tree), thuật toán chỉ di chuyển từ trạng thái hiện tại sang các trạng thái lân cận có giá trị tốt hơn dựa trên một **hàm mục tiêu (objective function)** hoặc hàm chi phí.
* **Ưu điểm vượt trội:** Tiết kiệm dung lượng bộ nhớ rất lớn (thường chỉ lưu trạng thái hiện tại hoặc một vài trạng thái) và xử lý hiệu quả trong các không gian trạng thái khổng lồ.

---

### 2. "Địa hình" Không gian Trạng thái (State-Space Landscape)

Local Search đánh giá trạng thái dựa trên một bề mặt địa hình giá trị (landscape). Do chỉ quan sát cục bộ ở các ô lân cận, thuật toán thường gặp phải các chướng ngại địa hình:
* **Local Maxima (Cực đại cục bộ):** Điểm có giá trị cao hơn tất cả các ô lân cận xung quanh, nhưng vẫn thấp hơn cực đại toàn cục (Global Maximum).
* **Plateaus (Vùng bằng phẳng):** Khu vực mà giá trị hàm mục tiêu không thay đổi giữa các ô lân cận. Địa hình này gồm:
  * *Flat local maximum:* Vùng phẳng đỉnh núi mà mọi hướng di chuyển xung quanh đều không làm tăng giá trị.
  * *Shoulder (Vai núi):* Vùng phẳng mà từ đó vẫn có đường tiếp tục đi lên cao.

---

### 3. Bốn Thuật toán Local Search Cốt lõi

#### 🔴 3.1 Hill-Climbing Search (Tìm kiếm Leo đồi / Steepest-Ascent)
* **Cơ chế:** Thuật toán liên tục di chuyển từ trạng thái hiện tại sang trạng thái lân cận có giá trị hàm mục tiêu tăng nhiều nhất. Quá trình dừng lại khi không có trạng thái lân cận nào tốt hơn trạng thái hiện tại.
* **Đánh giá:** Mang tính "tham ăn" (greedy) nên thuật toán không đảm bảo tính đầy đủ (incomplete) và rất dễ bị mắc kẹt vĩnh viễn ở các cực đại cục bộ hay vùng bằng phẳng.
* **Các biến thể cải tiến:**
  * *Stochastic Hill-Climbing:* Chọn ngẫu nhiên một trong các nước đi hướng lên, giúp hội tụ đến đỉnh cao hơn.
  * *Random Sideways Moves:* Cho phép di chuyển ngang trên các vùng phẳng (shoulders) để tìm cơ hội bứt phá.
  * *Random-Restart Hill-Climbing:* Thực hiện nhiều lượt leo đồi từ các trạng thái bắt đầu ngẫu nhiên khác nhau. Biến thể này đạt tính đầy đủ (complete) vì trạng thái khởi tạo ngẫu nhiên sẽ có lúc rơi vào vùng của cực đại toàn cục.
  * *Gradient Descent:* Khái niệm tương đương khi bài toán đòi hỏi **tối thiểu hóa hàm chi phí** thay vì tối đa hóa hàm mục tiêu.

#### 🟠 3.2 Simulated Annealing (Mô phỏng Luyện kim)
* **Cơ chế:** Kết hợp giữa di chuyển ngẫu nhiên (Random Walk) và leo đồi (Hill-Climbing) để vừa tìm kiếm hiệu quả vừa thoát khỏi các cực đại cục bộ.
* **Quy tắc chấp nhận nước đi:** Chọn một nước đi lân cận ngẫu nhiên ở mỗi bước. Nếu nước đi làm tăng giá trị mục tiêu, thuật toán luôn chấp nhận. Nếu nước đi làm giảm giá trị mục tiêu, thuật toán vẫn chấp nhận nó với xác suất $e^{\Delta E / T}$.
* **Lịch trình nhiệt độ (Schedule):** Tham số nhiệt độ $T$ bắt đầu ở mức cao (cho phép nhận nhiều nước đi kém) và giảm dần về 0 theo thời gian. Khi $T \to 0$, thuật toán hoạt động giống như Hill-Climbing thuần túy. Nếu nhiệt độ giảm đủ chậm, thuật toán sẽ tìm thấy cực đại toàn cục với xác suất tiến tới 1.

#### 🟡 3.3 Local Beam Search (Tìm kiếm Chùm cục bộ)
* **Cơ chế:** Duy trì song song **$k$ trạng thái** thay vì chỉ 1 trạng thái duy nhất.
* **Quy trình:** Bắt đầu bằng $k$ trạng thái khởi tạo ngẫu nhiên. Ở mỗi vòng lặp, thuật toán sinh ra tất cả các trạng thái con của cả $k$ trạng thái, sau đó chọn ra **$k$ trạng thái con tốt nhất toàn bộ** cho vòng lặp tiếp theo.
* **Sự chia sẻ thông tin:** Khác với việc chạy $k$ lượt Hill-Climbing độc lập, Local Beam Search chia sẻ thông tin giữa các luồng tìm kiếm: các luồng có giá trị cao sẽ thu hút tài nguyên tìm kiếm về khu vực tiềm năng đó.
* **Biến thể Stochastic Beam Search:** Chọn $k$ trạng thái con dựa trên xác suất tỉ lệ với chất lượng của chúng để tránh bị kẹt ở các vùng bằng phẳng.

#### 🟢 3.4 Genetic Algorithms (Thuật toán Di truyền - GA)
* **Cơ chế:** Là một biến thể của Local Beam Search lấy cảm hứng từ quá trình tiến hóa sinh học tự nhiên.
* **Biểu diễn:** Bắt đầu với một quần thể (population) gồm $k$ trạng thái ngẫu nhiên (gọi là các cá thể / individuals), trong đó mỗi cá thể được mã hóa thành một chuỗi ký tự trên một bảng chữ cái hữu hạn.
* **Quy trình tiến hóa:**
  1. *Fitness Function (Hàm thích nghi):* Đánh giá chất lượng của từng cá thể. Ví dụ với bài toán 8-Queens, hàm thích nghi là số cặp quân hậu không tấn công nhau.
  2. *Selection (Lựa chọn):* Lựa chọn các cặp cá thể cha mẹ để sinh sản với xác suất tỉ lệ thuận với giá trị hàm thích nghi.
  3. *Crossover (Lai ghép):* Chọn ngẫu nhiên một điểm cắt và kết hợp hai đoạn chuỗi của cha và mẹ để tạo ra cá thể con.
  4. *Mutation (Đột biến):* Biến đổi ngẫu nhiên một ký tự trong chuỗi cá thể con với một xác suất nhỏ độc lập.
* **Ưu điểm:** Phép lai ghép (crossover) cho phép kết hợp các khối ký tự chất lượng cao đã qua tiến hóa từ hai cá thể khác nhau để tạo ra lời giải đột phá.

---

💡 **Đến đây, chúng ta đã khép lại toàn bộ Chương 1: Search Algorithms. Tiếp theo, bạn có muốn bước sang Chương 2: Constraint Satisfaction Problems (CSPs) để học về bài toán thỏa mãn ràng buộc và các kỹ thuật như Backtracking, Forward Checking hay Arc Consistency (AC-3) không?**

---

# Chương 2: Constraint Satisfaction Problems (CSPs)
## 2.1 Constraint Satisfaction Problems**.

Khác với các bài toán tìm kiếm ở Chương 1 vốn thuộc loại **bài toán lập kế hoạch (planning problems)** — nơi tác tử quan tâm đến từng bước di chuyển để tới đích — bài toán CSP thuộc loại **bài toán nhận dạng (identification problems)**. Trong CSP, chúng ta chỉ quan tâm đến việc **nhận diện một cấu hình trạng thái thỏa mãn toàn bộ các điều kiện** mà không cần quan tâm đến trình tự các hành động để tạo nên cấu hình đó.

---

### 1. Ba thành phần định nghĩa một CSP

Một bài toán CSP được xác định chính xác bởi **3 yếu tố cốt lõi**:
1. **Tập các Biến (Variables - $X$):** Tập hợp $N$ biến $\{X_1, X_2, \dots, X_N\}$ cần được gán giá trị.
2. **Miền giá trị (Domain - $D$):** Tập hợp $\{x_1, x_2, \dots, x_d\}$ chứa tất cả các giá trị khả thi mà một biến có thể nhận.
3. **Tập các Ràng buộc (Constraints - $C$):** Các quy tắc hoặc giới hạn đối với giá trị của các biến (có thể liên quan đến một hoặc nhiều biến khác).

---

### 2. Trạng thái Gán giá trị một phần & Độ phức tạp

* **Partial Assignments (Gán giá trị một phần):** Trạng thái trong bài toán CSP được biểu diễn bằng một cấu hình mà trong đó một số biến đã được gán giá trị, còn các biến khác thì chưa. 
* **Độ phức tạp:** Các bài toán CSP thuộc nhóm **NP-hard**. Nếu có $N$ biến và mỗi biến có miền giá trị kích thước $d$, không gian trạng thái gán giá trị có thể lên tới $O(d^N)$. Tuy nhiên, nhờ cấu trúc ràng buộc rõ ràng, ta có thể khai thác cấu trúc này để giải bài toán hiệu quả hơn nhiều so với tìm kiếm mù.

---

### 3. Đồ thị Ràng buộc (Constraint Graphs) & Phân loại Ràng buộc

CSP thường được biểu diễn trực quan dưới dạng **Constraint Graph (Đồ thị Ràng buộc)**, trong đó các nút đại diện cho các biến và các cạnh đại diện cho các ràng buộc giữa chúng:

* **Unary Constraints (Ràng buộc đơn biến):** Chỉ liên quan đến 1 biến duy nhất (thường được dùng để cắt tỉa miền giá trị của biến đó trước khi vẽ đồ thị).
* **Binary Constraints (Ràng buộc nhị biến):** Liên quan đến 2 biến, được biểu diễn bằng các cạnh nối truyền thống trong đồ thị. *(Ví dụ: Bài toán Tô màu bản đồ nước Úc — hai bang kề nhau không được trùng màu).*
* **Higher-order Constraints (Ràng buộc bậc cao):** Liên quan đến 3 hoặc nhiều biến trở lên.

---

### 4. Ứng dụng mô hình hóa CSP cho Game Pipes và Hashi

Để nối tiếp cuộc thảo luận ở các phần trước, đây là cách ta đưa hai trò chơi **Pipes** và **Hashi** về dạng bài toán CSP chuẩn:

#### 🚰 Trò chơi Pipes (FreeNet) dưới dạng CSP:
* **Variables ($X$):** Mỗi ô trên lưới $N \times M$ là một biến $X_{ij}$.
* **Domain ($D$):** Góc xoay của ô $\{0^\circ, 90^\circ, 180^\circ, 270^\circ\}$.
* **Constraints ($C$):** 
  * *Binary Constraints:* Đối với hai ô kề nhau $X_{ij}$ và $X_{i, j+1}$, nếu cạnh tiếp giáp của $X_{ij}$ có đầu ống thì cạnh tiếp giáp của $X_{i, j+1}$ cũng phải có đầu ống tương ứng (và ngược lại).
  * *Global Constraint:* Toàn bộ mạng lưới phải tạo thành 1 cụm liên thông duy nhất và không chứa vòng kín.

#### 🌉 Trò chơi Hashi (Bridges) dưới dạng CSP:
* **Variables ($X$):** Số lượng cầu nối giữa mỗi cặp đảo kề nhau $I_a$ và $I_b$, kí hiệu $X_{ab}$.
* **Domain ($D$):** $\{0, 1, 2\}$ (không có cầu, cầu đơn, hoặc cầu đôi).
* **Constraints ($C$):**
  * *Unary/Local Constraints:* Tổng số cầu quanh đảo $I_a$ phải đúng bằng con số ghi trên đảo: $\sum_{b} X_{ab} = N_a$.
  * *Binary/Geometric Constraints:* Hai cây cầu không được cắt nhau trên mặt phẳng.
  * *Global Constraint:* Tất cả các hòn đảo phải tạo thành 1 đồ thị liên thông duy nhất.

---

💡 **Bây giờ bạn đã nắm rõ cách mô hình hóa bài toán thành CSP! Tiếp theo, bạn có muốn bước sang mục 2.2 Solving CSPs: Backtracking Search để xem cách thuật toán Backtracking giải quyết các bài toán này không?**