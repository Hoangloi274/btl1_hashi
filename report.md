
## 1. Giới thiệu bài toán Hashi

Trò chơi diễn ra trên một lưới gồm các "hòn đảo" mang con số từ 1 đến 8, trong đó mục tiêu của người chơi là nối toàn bộ các đảo thành một mạng lưới liên thông duy nhất bằng các cây cầu theo hướng ngang hoặc dọc. Mỗi đường nối chỉ chứa tối đa 2 cây cầu, các cầu không được cắt nhau và số lượng cầu kết nối vào mỗi đảo phải đúng bằng con số ghi trên đảo đó.

## 2. Problem Analysis

**Trạng thái bắt đầu (Start State):** Cấu hình ban đầu của lưới $N \times M$ chứa vị trí cố định của các hòn đảo và con số yêu cầu (từ 1 đến 8) ghi trên từng đảo. Tại thời điểm xuất phát, chưa có cây cầu nào được đặt.

**Không gian trạng thái (State Space):**
  * Tập hợp tất cả các cấu hình phân bố cầu khả thi trên bàn cờ. 
  * Mỗi trạng thái đại diện cho một cách gán số lượng cầu (0, 1 hoặc 2) cho các hành lang theo chiều ngang hoặc dọc giữa các cặp hòn đảo lân cận.

**Tập hợp các hành động (Actions):**
   * Tại một trạng thái, hành động khả thi là chọn một hành lang giữa hai hòn đảo $I_a$ và $I_b$ (nằm trên cùng hàng hoặc cùng cột, không bị đảo khác chắn) và **đặt thêm 1 cây cầu đơn (hoặc nâng cấp thành cầu đôi)** giữa hai đảo đó.
   * Điều kiện hành động hợp lệ: Cầu mới không được cắt ngang qua bất kỳ cây cầu nào đã có và số lượng cầu giữa $I_a, I_b$ sau khi đặt không vượt quá 2.

**Mô hình chuyển trạng thái (Transition Model):**
   * Hàm nhận vào trạng thái bàn cờ hiện tại $S$ và hành động đặt/thay đổi cầu giữa hai đảo $I_a, I_b$.
   * Trả về **trạng thái bàn cờ mới $S'$**, trong đó số lượng cầu giữa $I_a$ và $I_b$ tăng lên 1, trong khi toàn bộ các cầu khác trên bàn cờ giữ nguyên.

**Chi phí hành động (Action Cost):**
   * Mỗi lần thực hiện thao tác xây một cây cầu được tính chi phí đồng nhất là **1** (cost = 1). 
   * Tổng chi phí đường đi chính là tổng số cầu được đặt để đi từ bàn cờ trống ban đầu đến lời giải hoàn chỉnh.

 **Các ràng buộc:**

  * **Đúng số lượng cầu:** Tổng số cầu nối vào mỗi hòn đảo đúng bằng con số ghi trên hòn đảo đó.
  * **Giới hạn số lượng cầu** Giữa hai đảo có thể kết nối trực tiếp chỉ được phép có tối đa 2 cây cầu (cầu đơn hoặc cầu đôi)
  * **Hướng đi:** Cầu chỉ chạy theo chiều ngang hoặc chiều dọc, không cắt cầu khác.
  * **Tính liên thông hoàn toàn:** Tất cả các hòn đảo được kết nối với nhau thành một nhóm/đồ thị liên thông duy nhất (không có đảo hay cụm đảo nào bị cô lập).

---

## 3. Thiết kế giải thuật Blind Search

### 3.1 Depth-First Search (DFS) cho Hashiwokakero

#### 3.1.1 Đặt vấn đề và ý tưởng

Bài toán Hashiwokakero được mô hình hóa thành bài toán **gán giá trị** cho tập các hành lang (corridor). Mỗi hành lang $c$ chỉ nhận một trong ba giá trị:

$$
x_c \in \{0, 1, 2\}
$$

trong đó $0$ nghĩa là không có cầu, $1$ là cầu đơn, $2$ là cầu đôi.

Không gian trạng thái do đó có kích thước $3^{|C|}$, với $|C|$ là số hành lang. Với kích thước này, tìm kiếm mù thuần túy dễ bị bùng nổ tổ hợp. DFS được lựa chọn vì:
- Chỉ cần bộ nhớ tuyến tính theo độ sâu ($O(|C|)$).
- Dễ kết hợp các kỹ thuật cắt tỉa (pruning) và sắp xếp biến.

---

#### 3.1.2 Các thành phần cốt lõi của thuật toán

**1. Biến quyết định**  
Mỗi hành lang là một biến. Tập biến:

$$
X = \{x_{c_1}, x_{c_2}, \dots, x_{c_m}\}, \quad m = |C|
$$

**2. Miền giá trị**  
$$
D(x_c) = \{0, 1, 2\} \quad \forall c
$$

**3. Ràng buộc (được kiểm tra từng phần)**  
- Ràng buộc bậc (degree): với mọi đảo $i$,
  $$
  \sum_{c \ni i} x_c \le t_i
  $$
  (khi đã gán hết thì phải bằng $t_i$).
- Ràng buộc không giao cắt: không tồn tại hai hành lang khác hướng dùng chung một ô.
- Ràng buộc liên thông: đồ thị các đảo với các cạnh có $x_c > 0$ phải liên thông (chỉ kiểm tra ở nút lá).

**4. Chiến lược tìm kiếm**  
- Duyệt sâu theo thứ tự biến đã sắp xếp.
- Thử lần lượt các giá trị 0, 1, 2.
- Quay lui ngay khi phát hiện vi phạm ràng buộc cục bộ.

---

#### 3.1.3 Sắp xếp biến theo MRV (Minimum Remaining Value)

Trước khi tìm kiếm, danh sách hành lang được sắp xếp theo heuristic MRV:

$$
\text{priority}(c) = \big(\min(t_a, t_b),\ t_a + t_b\big)
$$

với $t_a, t_b$ là target của hai đảo đầu mút của hành lang $c$.

- Ưu tiên hành lang nối với đảo có target nhỏ (miền “chặt” hơn).
- Khi hành lang có $\min$ bằng nhau thì ưu tiên hành lang tổng target nhỏ hơn.
- Mục tiêu: phát hiện mâu thuẫn sớm, giảm kích thước cây tìm kiếm thực tế.

---

#### 3.1.4 Cơ chế quay lui (Backtracking)


**Ý tưởng**

  Thuật toán tiến hành gán giá trị cho các hành lang theo từng bước. Sau mỗi lần gán, trạng thái hiện tại sẽ được check các ràng buộc cục bộ (ví dụ như số cầu vượt quá mục tiêu, hình dạng cầu hợp lệ), thuật toán sẽ quay lui và thử giá trị khác.

**Điều kiện dừng**

  Thuật toán trả về nghiệm khi tất cả các đảo đều đạt đúng target và không còn dư cầu cần gán và thoả được điều kiện liên thông. Nếu không có lựa chọn hợp lệ nào còn lại, toàn bộ nhánh được loại bỏ.

---

#### 3.1.5 Cơ chế cắt tỉa (Pruning)

Tại mọi nút trung gian, thuật toán chỉ duy trì các gán nhất quán cục bộ:

      _respect_degrees: không đảo nào bị gán vượt target.
      _avoid_crossings: không có hai cầu cắt nhau.

Chỉ cần một ràng buộc bị vi phạm là toàn bộ nhánh con bị loại. Nhờ đó số nút thực tế được mở rộng giảm đáng kể.



#### 2.1.5 Phân tích độ phức tạp và nhận xét


| Tiêu chí | Đánh giá |
|----------|----------|
| **Tính đầy đủ** | Có  |
| **Tính tối ưu** | Không đảm bảo (trả về lời giải đầu tiên tìm thấy) |
| **Thời gian** | $O(3^m)$ trường hợp xấu nhất; thực tế nhỏ hơn nhờ MRV và pruning |
| **Không gian** | $O(m)$ (chỉ lưu đường gán hiện tại trên stack đệ quy) |
| **Ưu điểm** | Tiết kiệm bộ nhớ, dễ cài, kết hợp tốt với ràng buộc |
| **Nhược điểm** | Vẫn bùng nổ khi $m$ lớn|

---

### 3. Thiết kế giải thuật Heuristic Search




#### 4. Hiệu quả so với Uninformed Search

* Với **BFS / DFS**, việc duyệt một không gian trạng thái lên tới $4^{N \times M}$ làm thuật toán nhanh chóng bị bùng nổ bộ nhớ hoặc chìm vào các nhánh vô vọng.
* Với **A* Search**, nhờ có thông tin định hướng từ hàm $h(n)$ ("bàn cờ nào càng ít đầu hở thì càng được ưu tiên duyệt trước"), thuật toán sẽ **bỏ qua hầu hết các nhánh xoay sai** và đi thẳng tới cấu hình bàn cờ hoàn chỉnh.

---


Trong thuật toán A*, mỗi trạng thái bàn cờ Hashi $n$ được gán một giá trị ưu tiên:

$$f(n) = g(n) + h(n)$$

* **$g(n)$:** Chi phí thực tế tích lũy từ trạng thái bắt đầu (tổng số cây cầu đã được đặt trên bàn cờ tính đến thời điểm hiện tại).
* **$h(n)$:** Ước lượng chi phí (số cây cầu) còn phải đặt thêm từ trạng thái $n$ để hoàn thành toàn bộ bàn cờ.

---

#### 3.1 Đánh giá chất lượng hàm heuristic 
**Tính chấp nhận được (Admissible):**



#### 3. Thiết kế các Hàm Heuristic $h(n)$ cho Hashi 

##### Heuristic 1: Tổng số cầu còn thiếu trên các đảo (Bridge Deficit Heuristic)
Mỗi hòn đảo $i$ ghi một con số mục tiêu $N_i$, và hiện tại đang có $d_i$ cây cầu nối vào nó.
* **Cách tính:** Số cầu còn thiếu của đảo $i$ là $\max(0, N_i - d_i)$.

  Vì mỗi cây cầu khi được đặt giữa hai hòn đảo sẽ đóng góp 1 cầu cho mỗi đầu đảo (giúp làm giảm tổng độ thiếu hụt của cả bàn cờ tối đa 2 đơn vị):
  $$h_1(n) = \left\lceil \frac{\sum_i \max(0, N_i - d_i)}{2} \right\rceil$$
* **Tính chấp nhận được (Admissible):** Do mỗi bước đặt 1 cây cầu chỉ có thể giảm tối đa 2 đơn vị thiếu hụt trên toàn bản đồ, số lượng cầu thực tế $h^*(n)$ cần đặt chắc chắn không thể nhỏ hơn $h_1(n)$. Vì $0 \le h_1(n) \le h^*(n)$, hàm $h_1(n)$ thỏa mãn điều kiện **Admissibility**, đảm bảo A* luôn tìm ra lời giải tối ưu.

##### Heuristic 2: Số lượng thành phần liên thông (Disconnected Components Heuristic)
* **Quy tắc Hashi:** Tất cả các hòn đảo phải được kết nối với nhau thành **một đồ thị/nhóm liên thông duy nhất**.
* **Cách tính:** Nếu các cây cầu hiện tại đang chia bàn cờ thành $K$ cụm đảo độc lập, agent cần ít nhất $K - 1$ cây cầu nữa để nối tất cả các cụm này lại với nhau.
  $$h_2(n) = K - 1$$
* **Tính chấp nhận được (Admissible):** Để hợp nhất $K$ thành phần rời rạc thành 1 nhóm duy nhất, số cạnh (cầu) tối thiểu cần thêm vào luôn là $K - 1$.


##### Heuristic 3: Nút thắt cổ chai và giới hạn hướng đi (`bottleneck_corrected`)

* **Quy tắc Hashi:** Mỗi hòn đảo bị giới hạn bởi không gian vật lý xung quanh, chỉ có thể vươn ra một số hướng đi khả dụng nhất định.
* **Cách tính:**
  * Xét nhu cầu cầu còn thiếu của hòn đảo ($d$). 
  * Đếm số lượng hướng đi/hành lang lân cận còn khả dụng (`available_edges`).
  * Nếu nhu cầu của đảo vượt quá số hướng đi khả dụng ($d > \text{available\_edges}$), phần chênh lệch $\max(0, d - \text{available\_edges})$ chính là điểm nghẽn bắt buộc phải xây dựng cầu đôi (double bridges).


* **Công thức ước lượng:**

$$h_3(n) = \left\lceil \frac{1}{2} \sum_{i} \max\left(0, \text{demand}_i - \text{available\_edges}_i\right) \right\rceil$$


* **Ý nghĩa:** Giúp A* nhận diện trước các điểm nghẽn vật lý khắt khe trên lưới mà chỉ đếm số cầu thiếu đơn thuần không phản ánh hết.

##### Heuristic 4: Kết hợp Heuristic cực đại (Dominant Heuristic)

* Để tạo ra hàm heuristic mạnh nhất, ta lấy giá trị cực đại giữa tất cả các hàm heuristic chấp nhận được:

$$h(n) = \max\Big(h_1(n), h_2(n), h_3(n)\Big)$$


* Hàm $h(n)$ này vừa **Admissible** vừa **Dominant** (trội hơn các hàm thành phần), giúp thuật toán A* ước lượng sát chi phí thực tế hơn, nhận diện sớm các thế cục hiểm nghèo và loại bỏ bớt nhiều nhánh tìm kiếm không cần thiết.
---

#### 3. Kỹ thuật Cắt tỉa trạng thái chết (Deadlock Pruning)

Trò chơi Hashi có đặc thù là một bước đặt cầu sai có thể làm "chết" các hòn đảo xung quanh. Do đó, ta áp dụng kỹ thuật cắt tỉa sớm:
* **Phát hiện trạng thái vi phạm:** Nếu một hành động đặt cầu khiến tổng số cầu của một đảo vượt quá con số yêu cầu ($d_i > N_i$), hoặc làm hai cây cầu cắt nhau, hoặc tạo ra một cụm đảo cô lập đã đủ cầu nhưng chưa nối với phần còn lại của bàn cờ, trạng thái đó là không hợp lệ.
* **Gán chi phí vô cùng:** Ta gán $h(n) = \infty$ cho các trạng thái này để A* loại bỏ ngay lập tức khỏi Frontier.

---

#### 4. Quy trình thực thi A* Search trên Hashi

1. **Khởi tạo Frontier:** Đưa bàn cờ ban đầu (chưa có cây cầu nào) vào **Priority Queue**, sắp xếp ưu tiên theo giá trị $f(n) = g(n) + h(n)$ nhỏ nhất.
2. **Chọn nút mở rộng:** Lấy trạng thái bàn cờ có $f(n)$ nhỏ nhất ra khỏi Frontier.
3. **Mở rộng (Expand):** Tìm các cặp đảo kề nhau theo chiều ngang/dọc chưa bị chặn và sinh các trạng thái con bằng cách đặt 1 cầu đơn hoặc cầu đôi.
4. **Graph Search Optimization:** Duy trì tập `reached` để lưu các cấu hình phân bố cầu đã duyệt cùng chi phí $g(n)$ nhỏ nhất, tránh việc lặp lại các chu trình thử-xóa cầu.
5. **Kiểm tra Goal:** Thuật toán dừng khi lấy ra trạng thái có $h(n) = 0$ (mọi hòn đảo đều đạt đúng số cầu yêu cầu và toàn bộ bàn cờ liên thông hoàn toàn).

---

#### 5. So sánh hiệu quả với Uninformed Search

* **DFS / BFS:** Dễ rơi vào tình trạng bùng nổ tổ hợp do số lượng cặp đảo có thể nối là rất lớn, dẫn tới việc tìm kiếm vô hướng và dễ bị nghẽn bộ nhớ.
* **A\* Search:** Nhờ hàm $h(n)$ định hướng ("bàn cờ nào còn ít thiếu hụt cầu và ít bị phân mảnh cụm nhất sẽ được ưu tiên duyệt trước"), A* sẽ tập trung thẳng vào các nước đi chính xác và hoàn thành câu đố nhanh hơn đáng kể.

---
### Quy trình hiện thực hóa 

### 1. Mô hình trạng thái tĩnh:

Những thứ ko thay đổi trong suốt quá trình giải

- File grid.py

      class Island: 
          tọa độ
          capacity
                        ??số cầu hiện tại 
      class Corridor (Các cạnh nối 2 đảo trên cùng hàng/cột):
          island_a
          island_b
          hướng đi      ??len xuống, hàng cột mấy
          các hành lang cắt ngang nó
      class Grid (lưới bàn cờ):
          Island
          Corridor


### 2. Mô hình trạng thái động:

- File state.py

Nh trạng thái thay đổi sau mỗi bước di chuyển của solver

        dist bridge_counts
            bridge_counts (số cầu trên mỗi hành lang)
            remaining_degree (số cầu hiện tại của mỗi đảo)
            apply_action (hàm tạo trạng thái con mới khi đặt thêm 1 cầu)
            --hash--,--eq-- (hàm mã hóa trạng thái để thuật toán A* check xem trạng thái này đã đc duyệt qua trong Closed Set hay chưa)     ??cùng trạng thái nh khác hướng cầu thì sao

  ---
        **Set-Dict,__hash__,__eq__** (magic method)

          **Set** lưu trữ là khóa của **dict**
          __hash__ hàm băm              ??lấy key là gì bỏ vào set
          __eq__(self, other) giải quyết đụng độ, xem trạng thái này đã đc thêm vào set chưa          

### 3. Kiểm tra thỏa ràng buộc

- File checker.py

      hàm kiểm tra cục bộ (kt xem việc đặt cầu có phá ràng buộc nào ko)
      hàm kt toàn cục /is_solved/ (kt xem đã giải xong ch) ??kt tính liên thông Union-Find (làm j)


### 4. Thuật toán

- Solvers/ (astar.py, backtracking.py,..,)

  - astar.py
        Priority Queue (dùng /heapq/ của Python để lưu các trạng thái chờ duyệt dựa trên hàm chi phí f=g+h)
        Hàm Heuristic 
            /deficit/ số cầu còn thiếu
            /min_conn/ số TP liên thông
            /bottleneck_corrected/ nhận diện trước các điểm nghẽn
        Vòng lặp tìm kiếm: lấy node có min f -> kiểm tra đích -> sinh các trạng thái con -> đẩy vào heap

  - backtracking.py

### 5. Nhập/ Xuất dữ liệu (Đọc file input, ghi output)

- File loader.py, renderer.py 
    Xử lý giao tiếp với tg bên ngoài (đọc file từ thư mục Inputs/ và in ra kết quả cho người dùng xem)

    - loader.py: Chuyển dl file thành các đối tượng Island, Corridors  trong Grid
    - renderer.py: In bàn cờ ra màn hình Console 

---




                        

