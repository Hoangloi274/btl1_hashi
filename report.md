
## 1. Giới thiệu bài toán Hashi

Trò chơi diễn ra trên một lưới gồm các "hòn đảo" mang con số từ 1 đến 8, trong đó mục tiêu của người chơi là nối toàn bộ các đảo thành một mạng lưới liên thông duy nhất bằng các cây cầu theo hướng ngang hoặc dọc. Mỗi đường nối chỉ chứa tối đa 2 cây cầu, các cầu không được cắt nhau và số lượng cầu kết nối vào mỗi đảo phải đúng bằng con số ghi trên đảo đó.

## 2. Problem Analysis

**Trạng thái bắt đầu (Start State):** Cấu hình ban đầu của lưới $N \times M$ chứa vị trí cố định của các hòn đảo và con số yêu cầu (từ 1 đến 8) ghi trên từng đảo. Tại thời điểm xuất phát, chưa có cây cầu nào được đặt.

**Không gian trạng thái (State Space):**
  
  Tập hợp tất cả các cấu hình phân bố cầu khả thi trên bàn cờ. 
  Mỗi trạng thái đại diện cho một cách gán số lượng cầu (0, 1 hoặc 2) cho các hành lang theo chiều ngang hoặc dọc giữa các cặp hòn đảo lân cận.

**Tập hợp các hành động (Actions):**

  Tại một trạng thái, hành động khả thi là chọn một hành lang giữa hai hòn đảo $I_a$ và $I_b$ (nằm trên cùng hàng hoặc cùng cột, không bị đảo khác chắn) và đặt thêm 1 cây cầu đơn (hoặc nâng cấp thành cầu đôi) giữa hai đảo đó.

  Điều kiện hành động hợp lệ: Cầu mới không được cắt ngang qua bất kỳ cây cầu nào đã có và số lượng cầu giữa $I_a, I_b$ sau khi đặt không vượt quá 2.

**Mô hình chuyển trạng thái (Transition Model):**

   Hàm nhận vào trạng thái bàn cờ hiện tại $S$ và hành động đặt/thay đổi cầu giữa hai đảo $I_a, I_b$.

   Trả về trạng thái bàn cờ mới $S'$, trong đó số lượng cầu giữa $I_a$ và $I_b$ tăng lên 1, trong khi toàn bộ các cầu khác trên bàn cờ giữ nguyên.

**Chi phí hành động (Action Cost):**

   Mỗi lần thực hiện thao tác xây một cây cầu được tính chi phí đồng nhất là **1** (cost = 1). 

   Tổng chi phí đường đi chính là tổng số cầu được đặt để đi từ bàn cờ trống ban đầu đến lời giải hoàn chỉnh.

 **Các ràng buộc:**

  Đúng số lượng cầu: Tổng số cầu nối vào mỗi hòn đảo đúng bằng con số ghi trên hòn đảo đó.

  Giới hạn số lượng cầu: Giữa hai đảo có thể kết nối trực tiếp chỉ được phép có tối đa 2 cây cầu (cầu đơn hoặc cầu đôi)

  Hướng đi: Cầu chỉ chạy theo chiều ngang hoặc chiều dọc, không cắt cầu khác.

  Tính liên thông hoàn toàn: Tất cả các hòn đảo được kết nối với nhau thành một nhóm/đồ thị liên thông duy nhất (không có đảo hay cụm đảo nào bị cô lập).

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

Trong thuật toán A*, mỗi trạng thái bàn cờ Hashi $n$ được gán một giá trị ưu tiên:

$$f(n) = g(n) + h(n)$$

* **$g(n)$:** Chi phí thực tế tích lũy từ trạng thái bắt đầu (tổng số cây cầu đã được đặt trên bàn cờ tính đến thời điểm hiện tại).
* **$h(n)$:** Ước lượng chi phí (số cây cầu) còn phải đặt thêm từ trạng thái $n$ để hoàn thành toàn bộ bàn cờ.

---

#### 3.1 Đánh giá chất lượng hàm heuristic 
**Tính chấp nhận được (Admissibility):**

Một hàm heuristic $h(n)$ được gọi là chấp nhận được nếu với mọi nút $n$, giá trị ước lượng của nó không bao giờ âm và không bao giờ vượt quá chi phí thực tế tối ưu để đi từ nút $n$ đến đích $h^*(n)$.

$$\forall n, \quad 0 \le h(n) \le h^*(n)$$



trong đó:
* $h(n)$: Chi phí ước lượng từ nút $n$ đến đích.
* $h^*(n)$: Chi phí tối ưu thực tế từ nút $n$ đến đích.


Đảm bảo tính tối ưu (Optimality): Nếu sử dụng một heuristic thỏa mãn tính chất admissible trong A* Tree Search, thuật toán được đảm bảo sẽ tìm ra đường đi có tổng chi phí thấp nhất (đường đi tối ưu).

**Tính nhất quán (Consistence)**

Một hàm heuristic $h(n)$ được gọi là consistent nếu với mọi nút $n$ và mọi nút con $n'$ của nó (được sinh ra qua một hành động có chi phí $cost(n, n')$), ước lượng khoảng cách từ $n$ đến đích không vượt quá chi phí để đi đến $n'$ cộng với ước lượng khoảng cách từ $n'$ đến đích.

$$h(n) \le cost(n, n') + h(n')$$
Với mọi nút đích $G$, giá trị heuristic luôn bằng 0: $h(G) = 0$.

Nếu heuristic đạt chuẩn consistent, thuật toán được đảm bảo sẽ tìm thấy đường đi tối ưu ngay lần đầu tiên chạm tới mỗi nút mà không cần phải quay lại cập nhật đường đi ngắn hơn.

**Tính trội (Dominance)**

Heuristic $h_a$ được coi là trội hơn ($h_a$ dominates $h_b$) heuristic $h_b$ nếu với mọi nút $n$ trong không gian trạng thái, giá trị ước lượng của $h_a(n)$ luôn lớn hơn hoặc bằng $h_b(n)$.

$$\forall n, \quad h_a(n) \ge h_b(n)$$


  Heuristic nào có giá trị lớn hơn nhưng vẫn thỏa mãn điều kiện admissible sẽ mô phỏng sát với chi phí thực tế hơn, giúp A* định hướng tìm kiếm tập trung vào đích nhanh hơn và phải mở rộng ít nút hơn so với heuristic nhỏ hơn.

  Hàm max của nhiều heuristic admissible ($\max(h_a, h_b)$) cũng sẽ là một heuristic admissible và nó sẽ trội hơn (tốt hơn) cả hai thành phần $h_a$ và $h_b$ đứng độc lập.



#### 3.2 Thiết kế các Hàm Heuristic $h(n)$ cho Hashiwokakero 

##### Heuristic 1: Tổng số cầu còn thiếu trên các đảo (Bridge Deficit Heuristic)
Mỗi hòn đảo $i$ ghi một con số mục tiêu $N_i$, và hiện tại đang có $d_i$ cây cầu nối vào nó.

Cách tính: Số cầu còn thiếu của đảo $i$ là $\max(0, N_i - d_i)$.

  Vì mỗi cây cầu khi được đặt giữa hai hòn đảo sẽ đóng góp 1 cầu cho mỗi đầu đảo (giúp làm giảm tổng độ thiếu hụt của cả bàn cờ tối đa 2 đơn vị):
  $$h_1(n) = \left\lceil \frac{\sum_i \max(0, N_i - d_i)}{2} \right\rceil$$

Do mỗi bước đặt 1 cây cầu chỉ có thể giảm tối đa 2 đơn vị thiếu hụt trên toàn bản đồ, số lượng cầu thực tế $h^*(n)$ cần đặt chắc chắn không thể nhỏ hơn $h_1(n)$. Vì $0 \le h_1(n) \le h^*(n)$, hàm $h_1(n)$ thỏa mãn điều kiện chấp nhận được, đảm bảo A* luôn tìm ra lời giải tối ưu.

##### Heuristic 2: Số lượng thành phần liên thông (Disconnected Components Heuristic)

Tất cả các hòn đảo phải được kết nối với nhau thành một đồ thị liên thông duy nhất.

Cách tính: Nếu các cây cầu hiện tại đang chia bàn cờ thành $K$ cụm đảo độc lập, agent cần ít nhất $K - 1$ cây cầu nữa để nối tất cả các cụm này lại với nhau.

  $$h_2(n) = K - 1$$

Luôn thỏa mãn tính chấp nhận được

##### Heuristic 3: Nút thắt cổ chai và giới hạn hướng đi 

Mỗi hòn đảo bị giới hạn bởi không gian vật lý xung quanh, chỉ có thể đặt cầu ở một số hướng đi khả dụng nhất định.

Cách tính:

  * Số cầu còn thiếu của đảo ($X_i = N_i - d_i$). 
  * Đếm số lượng hành lang lân cận còn khả dụng ($r_i$).
  * Nếu nhu cầu của đảo vượt quá số hướng đi khả dụng ($X > r$), phần chênh lệch $\max(0, X - r)$ chính là điểm nghẽn bắt buộc phải xây dựng cầu đôi.


$$h_3(n) = \left\lceil \frac{1}{2} \sum_{i} \max\left(0, N_i - d_i - r_i\right) \right\rceil \le \left\lceil \frac{1}{2} \sum_{i} \max\left(0, N_i - d_i\right) \right\rceil \le h_1(n) $$


Giúp A* nhận diện trước các điểm nghẽn vật lý khắt khe trên lưới mà chỉ đếm số cầu thiếu đơn thuần không phản ánh hết, kế thừa tính chấp nhận được từ $h_1$



##### Heuristic 4: Kết hợp Heuristic cực đại (Dominant Heuristic)

Để tạo ra hàm heuristic mạnh nhất, ta lấy giá trị cực đại giữa tất cả các hàm heuristic chấp nhận được:

$$h(n) = \max\Big(h_1(n), h_2(n), h_3(n)\Big)$$


Hàm $h(n)$ này vừa Admissible vừa Dominant (trội hơn các hàm thành phần), giúp thuật toán A* ước lượng sát chi phí thực tế hơn, nhận diện sớm các thế cục hiểm nghèo và loại bỏ bớt nhiều nhánh tìm kiếm không cần thiết.

---

#### 3.3 Phân tích độ phức tạp và nhận xét

| Tiêu chí | Đánh giá |
|----------|----------|
| **Tính đầy đủ** | Có. Với heuristic admissible, A* đảm bảo tìm thấy lời giải nếu tồn tại  |
| **Tính tối ưu** | Có, lời giải trả về là tối ưu theo hàm chi phí|
| **Thời gian** | $O({(b^*)}^m)$ ( $1 \le b\ll 3$) với các heuristic mạnh, không gian tìm kiếm được cắt tỉa đáng kể |
| **Không gian** | $O(3^m)$ |
| **Ưu điểm** | Đảm bảo lời giải tối ưu <br> Khả năng mở rộng trên lưới trung bình/lớn|
| **Nhược điểm** | Tốn bộ nhớ|
---

### 4. Mô hình thực nghiệm

Các bài toán được phân loại theo kích thước lưới và mật độ đảo. Bảng 4.1 chi tiết các thông số thiết lập cho test case
<center>
 Bảng 4.1: Thông số cấu hình chi tiết cho các bộ test case 
</center>

|Kích thước lưới| Số lượng đảo (min – max) |
|-----------|----------|
|7x7 | 10-15  |
| 9x9 | 25-30|
| 11x11 | 30-35|
| 13x13 | 30-35 |
| **Ưu điểm** | Đảm bảo lời giải tối ưu <br> Khả năng mở rộng trên lưới trung bình/lớn|
| **Nhược điểm** | Tốn bộ nhớ|

### 5. Phân tích và Nhận xét

Để đánh giá và so sánh hiệu quả của các thuật toán, nhóm sử dụng các thước đo định lượng sau:

**Thời gian thực thi:** Sử dụng hàm `time.perf_counter()` trong Python

**Số nút đã duyệt:** Số lượng trạng thái mà thuật toán đã lấy ra khỏi hàng đợi ưu tiên (nếu là A*) hoặc số lần gọi đệ quy (nếu là Backtracking).

**Bộ nhớ sử dụng:** Lượng bộ nhớ RAM tối đa mà thuật toán chiếm dụng, đo bằng thư viện `tracemalloc`.   



| Grid size | Islands | Total Bridges | Algorithm | Time (s) | Mem (MB) | Nodes |
| :---: | :---: | :---: | :------- | :--- | :--- | :--- |
| **7x7** | 13 | 32 |  <span style="display:inline-block; width:100px;"> A* (Composite)  <br>DFS | 0.0268<br>24.5085 | 0.08<br>0.00 | 44<br>358853 |
| **7x7** | 14 | 38 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.0125<br>54.7000 | 0.05<br>0.00 | 51<br>754514 |
| **7x7** | 13 | 32 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.0088<br>15.9173 | 0.05<br>0.00 | 44<br>261906 |
| **9x9** | 26 | 72 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.3180<br>SKIPPED | 0.73<br>0.00 | 679<br>0 |
| **9x9** | 25 | 58 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.4413<br>SKIPPED | 0.80<br>0.00 | 907<br>0 |
| **9x9** | 25 | 58 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.2521<br>SKIPPED | 0.45<br>0.00 | 551<br>0 |
| **11x11** | 31 | 90 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 2.6227<br>SKIPPED | 4.49<br>0.00 | 4294<br>0 |
| **11x11** | 31 | 82 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 10.3402<br>SKIPPED | 25.36<br>0.00 | 17745<br>0 |
| **11x11** | 33 | 92 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 1.2792<br>SKIPPED | 2.45<br>0.00 | 2105<br>0 |
| **13x13** | 31 | 80 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 0.5894<br>SKIPPED | 1.39<br>0.00 | 1069<br>0 |
| **13x13** | 33 | 102 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 3.1314<br>SKIPPED | 5.12<br>0.00 | 5124<br>0 |
| **13x13** | 33 | 108 | <span style="display:inline-block; width:100px;"> A* (Composite) <br>DFS | 2.5966<br>SKIPPED | 4.52<br>0.00 | 4031<br>0 |

#### 5.1 Tác động cúa số lượng đảo

Số lượng đảo là yếu tố trực tiếp nhất ảnh hưởng đến độ phức tạp của bài toán Hashiwokakero.

![alt text](image-1.png)
<center>
Bảng 4.2: Thời gian theo số lượng đảo 
</center>

![alt text](image-2.png)
<center>
Bảng 4.3: Thời gian theo số lượng đảo (Log Scale)
</center>

![alt text](image-3.png)
<center>
Bảng 4.4: Số lượng nút duyệt theo số lượng đảo 
</center>

![alt text](image-4.png)
<center>
Bảng 4.5: Bộ nhớ theo số lượng đảo
</center>

![alt text](image-6.png)
<center>
Bảng 4.6: Bộ nhớ theo số lượng đảo (Log Scale)
</center>

**Thời gian thực thi:** 
- Hình 4.2, ta thấy thời gian chạy của tất cả các thuật toán đều tăng vọt khi số lượng đảo tăng
- Trên biểu đồ Logarit (Hình 4.3), độ dốc của đường A* (Composite) thấp hơn đáng kể so với DFS. Điều này chứng tỏ hàm Heuristic đã ước lượng tốt chi phí, giúp giảm cơ số của hàm mũ và cho phép thuật toán tiếp cận được các bài toán có kích thước lớn hơn.

**Không gian:** 

Hình 4.4 minh họa sự chênh lệch cực lớn giữa số
nút phải duyệt giữa DFS với các thuật toán Heuristic. Trong khi Backtracking lãng phí tài nguyên vào các nhánh vô vọng, A* với Heuristic tốt tập trung mở rộng các nút tiềm năng, giảm
thiểu đáng kể không gian tìm kiếm.

**Bộ nhớ:**

- DFS cho mức tiêu hao bộ nhớ thấp và ổn định trong khi A* phải lưu trữ toàn bộ tập Open và Closed để đảm bảo tính tối ưu, dẫn
đến việc tiêu thụ bộ nhớ tăng nhanh theo số lượng đảo.

- Với bài toán có số lượng lớn đảo (>40), A* có xu hướng
gặp lỗi tràn bộ nhớ trước khi hết thời gian cho phép.

#### 5.2 Tác động của kích thước lưới

Kích thước lưới (Grid Size) cũng ảnh hưởng đến độ phức tạp

![alt text](image-7.png)
<center>
Bảng 4.7: Thời gian theo kích thước lưới
</center>

![alt text](image-8.png)
<center>
Bảng 4.8: Thời gian theo kích thước lưới (Log Scale)
</center>

Khi kích thước lưới tăng nhưng mật độ đảo giữ nguyên, bài toán
có thể trở nên dễ hơn do giảm bớt các ràng buộc chéo (crossing constraints). Tuy nhiên, không gian tìm kiếm vẫn mở rộng do độ dài đường đi tăng lên.

Hình 4.7 cho thấy độ phân tán dữ liệu lớn hơn nhiều so với biểu
đồ theo số đảo. Cho thấy vị trí tương đối của các đảo có ảnh hưởng đến độ khó.

#### 5.3 Mức độ hiệu quả của các thuật toán Heuristic

![alt text](image-9.png)
<center>
Bảng 4.8: So sánh thời gian thực thi giữa các Heuristic 
</center>

![alt text](image-10.png)
<center>
Bảng 4.9: So sánh số nút duyệt giữa các Heuristic 
</center>

Về số nút mở rộng, Composite Heuristic cho kết quả tốt nhất nhờ cận dưới chặt. Tuy nhiên, về thời gian thực thi trung bình, Deficit Heuristic vượt trội vì chi phí đánh giá thấp hơn. Composite phải tính đồng thời ba heuristic thành phần nên overhead lớn hơn, dẫn đến tổng thời gian cao hơn dù ít nút hơn. Điều này thể hiện rõ sự đánh đổi giữa độ chặt của heuristic và chi phí tính toán tại mỗi nút.

### 6. Kết luận

Trong đồ án này, nhóm đã mô hình hóa bài toán Hashiwokakero dưới dạng bài toán tìm kiếm trong không gian trạng thái và hiện thực hai nhóm giải thuật đại diện: tìm kiếm mù (DFS/Backtracking) và tìm kiếm có thông tin (A* với các heuristic chuyên biệt).

Về phía DFS, thuật toán được xây dựng theo cơ chế Backtracking kết hợp sắp xếp biến theo MRV và cắt tỉa sớm dựa trên ràng buộc bậc cùng ràng buộc không giao cắt. Giải thuật đảm bảo tính đầy đủ trên không gian hữu hạn, sử dụng bộ nhớ rất thấp \(O(|C|)\), nhưng không đảm bảo tính tối ưu và dễ bùng nổ tổ hợp khi số hành lang tăng. Thực nghiệm cho thấy DFS chỉ phù hợp với các lưới kích thước nhỏ (thường \(N \le 7\)).

Về phía A*, nhóm đề xuất và chứng minh bốn heuristic: Deficit, Disconnected Components, Local Bottleneck và Composite. Cả bốn heuristic đều thỏa mãn tính chấp nhận được, nhờ đó A* bảo đảm tìm được lời giải tối ưu. Kết quả thực nghiệm cho thấy:

- Composite cho cận dưới chặt nhất, giúp giảm mạnh số nút mở rộng
- Deficit có chi phí đánh giá thấp nhất nên thường đạt thời gian chạy tốt nhất trên bộ test
- A* mở rộng được sang các lưới lớn hơn rõ rệt so với DFS, thể hiện ưu thế của việc tận dụng tri thức miền.

Sự so sánh giữa hai hướng tiếp cận làm rõ mối quan hệ đánh đổi trong tìm kiếm: DFS ưu tiên tiết kiệm bộ nhớ và sự đơn giản; A* ưu tiên chất lượng lời giải và khả năng cắt tỉa không gian trạng thái. Với bài toán Hashi, khi luật chơi chỉ yêu cầu một cấu hình hợp lệ, cả hai đều có thể trả về nghiệm đúng; tuy nhiên nếu xét hiệu năng tổng thể và khả năng mở rộng, A* với heuristic phù hợp là lựa chọn vượt trội.

Hướng phát triển tiếp theo có thể gồm: tinh chỉnh thêm heuristic (ví dụ kết hợp thông tin luồng hoặc ràng buộc toàn cục chặt hơn), tích hợp forward checking sâu hơn vào A*, mở rộng thử nghiệm trên bộ dữ liệu lớn hơn, và hoàn thiện giao diện tương tác để hỗ trợ người chơi cũng như trực quan hóa quá trình tìm kiếm của từng giải thuật.


## Tài liệu tham khảo

[1] Berkeley Artificial Intelligence Group, CS 188: Introduction to Artificial Intelligence (Textbook), University of California, Berkeley. https://inst.eecs.berkeley.edu/~cs188/textbook/

[2] GeeksforGeeks, Backtracking algorithms. https://www.geeksforgeeks.org/dsa/backtracking-algorithms/

[3] GeeksforGeeks, State space search in AI. https://www.geeksforgeeks.org/artificial-intelligence/state-space-search-in-ai/

[4] D. Poole and A. Mackworth, Artificial Intelligence: Foundations of Computational Agents, 3rd ed. Cambridge University Press, 2017, ch. 3, sec. 3.7. https://artint.info/3e/html/ArtInt3e.Ch3.S7.html
