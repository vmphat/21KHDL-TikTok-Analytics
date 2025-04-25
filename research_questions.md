# User Dashboard 1: Correlation analysis

RQ1: "Với cùng một ngưỡng số người theo dõi nhất định, liệu việc tăng số lượng video có thực sự đem lại nhiều lượt thích hơn trên mỗi video, hay chỉ đơn thuần tạo ra nhiều lượt thích tổng?"

### Nhận xét scatter matrix + heatmap

- Trong dữ liệu về các TikToker, mối quan hệ giữa số người theo dõi, số lượt thích và số lượng video thể hiện một số xu hướng đáng chú ý. Mức độ tương quan giữa số người theo dõi và số lượt thích là rất cao (0.93), cho thấy sự tăng trưởng của hai chỉ số này đi đôi với nhau. Các TikToker có lượng người theo dõi lớn thường nhận được nhiều lượt thích hơn, điều này khá hợp lý vì lượng fan đông đảo thường đồng nghĩa với sự yêu thích cao hơn dành cho nội dung.

- Trong khi đó, hệ số tương quan giữa số lượng video và hai chỉ số trên thấp hơn nhiều. Điều này cho thấy rằng số lượng video không quyết định trực tiếp đến số lượng người theo dõi hay lượt thích. Tuy nhiên, có thể thấy sự tương quan tích cực, với hệ số 0.42 và 0.47, cho thấy những người tạo ra nhiều video hơn có xu hướng thu hút nhiều người theo dõi và lượt thích hơn, nhưng không phải là yếu tố quyết định. Nhìn chung, sự tương quan mạnh mẽ nhất là giữa số người theo dõi và số lượt thích, phản ánh tầm quan trọng của sự tương tác và sự yêu thích của khán giả đối với sự thành công trên nền tảng.

# User Dashboard 2: Theo nhóm Tiktoker có mức Follower khác nhau

## RQ: Liệu việc tăng số lượng video có thực sự đem lại nhiều lượt xem và lượt tương tác hơn trên mỗi video?

### 1. Số video vs Số lượt xem

Mối quan hệ: Hệ số tương quan âm (-0.38) cho thấy mối quan hệ tương quan nghịch giữa số lượng video và số lượt xem trên mỗi video. Điều này có nghĩa là khi một TikToker đăng nhiều video hơn, số lượt xem trung bình trên mỗi video có xu hướng giảm.

Đường xu hướng (trend line): Đường xu hướng màu đỏ trên biểu đồ thể hiện rõ xu hướng giảm của số lượt xem trên mỗi video khi số lượng video tăng lên.

TikToker thành công (góc trên bên trái): Các TikToker có ít video nhưng lượt xem cao (góc trên bên trái) thường có nội dung chất lượng, thu hút và có thể đã tìm được thị trường ngách thành công. Họ có thể tập trung vào việc tạo ra những video chất lượng cao, được đầu tư kỹ lưỡng thay vì đăng tải nhiều video một cách tràn lan.

Chiến lược phù hợp: Đối với nhóm TikToker này, chiến lược phù hợp là tập trung vào chất lượng hơn số lượng. Nên đầu tư thời gian và công sức vào việc tạo ra những video có giá trị, hấp dẫn, tối ưu hóa nội dung và thời gian đăng tải để thu hút và giữ chân người xem.

### 2. Số video vs Số lượt thích

Hệ số tương quan ρ = -0.37 cho thấy mối quan hệ tương quan nghịch yếu giữa số lượng video và số lượt thích trên mỗi video. Điều này có nghĩa là, khi số lượng video tăng, số lượt thích trên mỗi video có xu hướng giảm nhẹ, và ngược lại.

Đường xu hướng màu đỏ thể hiện xu hướng giảm. Điều này củng cố kết luận trên, cho thấy sự giảm nhẹ về số lượt thích khi số lượng video tăng.

Các TikToker ở góc trên bên trái (ít video, nhiều lượt thích) có thể đang tập trung vào việc sản xuất nội dung chất lượng cao, được đầu tư kỹ lưỡng và có thể có khả năng tương tác tốt với khán giả của họ.

Chiến lược phù hợp cho nhóm này là tập trung vào chất lượng hơn số lượng. Họ nên ưu tiên tạo ra những video chất lượng cao, hấp dẫn, đồng thời tối ưu hóa tương tác với người xem để duy trì và tăng lượt thích, thay vì đăng tải nhiều video với nội dung có thể bị loãng.

### 3. Số video vs Số bình luận

Hệ số tương quan ρ = -0.24 cho thấy mối quan hệ tương quan nghịch yếu giữa số lượng video và số lượt bình luận trên mỗi video. Điều này có nghĩa là khi số lượng video tăng lên, số lượt bình luận trên mỗi video có xu hướng giảm nhẹ.
Đường xu hướng màu đỏ thể hiện xu hướng giảm, củng cố thêm nhận định về mối quan hệ nghịch trên.
Các TikToker có ít video nhưng nhiều lượt bình luận (góc trên bên trái) thường tập trung vào việc tạo ra nội dung chất lượng cao, có tính tương tác mạnh mẽ, thu hút sự chú ý của khán giả. Họ có thể đầu tư nhiều thời gian hơn vào việc sản xuất và quảng bá cho từng video.
Chiến lược phù hợp với nhóm này là tập trung vào chất lượng thay vì số lượng. Họ nên tiếp tục tạo ra nội dung hấp dẫn, tương tác, đầu tư vào việc tương tác với người xem để tăng cường sự gắn kết và giữ chân khán giả.

### 4. Số video vs Số lượt chia sẻ

Hệ số tương quan: ρ = -0.11 cho thấy một mối quan hệ tương quan âm rất yếu. Điều này có nghĩa là, nhìn chung, khi số lượng video tăng lên, số lượt chia sẻ trên mỗi video có xu hướng giảm nhẹ, nhưng mối quan hệ này không đáng kể.

Đường xu hướng: Đường xu hướng màu đỏ thể hiện xu hướng giảm nhẹ. Tuy nhiên, do hệ số tương quan thấp, đường này chỉ mang tính chất minh họa, không phản ánh một mối quan hệ rõ rệt.

TikToker góc trên bên trái: Các TikToker có ít video nhưng số lượt chia sẻ cao có thể đang tập trung vào chất lượng nội dung hơn số lượng. Họ có thể tạo ra các video có giá trị cao, hấp dẫn, dễ chia sẻ, có thể là video độc đáo, sáng tạo hoặc giải quyết một vấn đề cụ thể.

Chiến lược phù hợp: Với nhóm này, chiến lược nên tập trung vào chất lượng nội dung. Ưu tiên sản xuất các video chất lượng cao, có giá trị, dễ chia sẻ, thay vì cố gắng tăng số lượng video một cách ồ ạt. Tối ưu hóa nội dung để tăng tương tác và chia sẻ, tập trung vào các chủ đề thu hút đối tượng mục tiêu.

### Kết luận chung

**Kết quả phân tích chính và Nhận xét tổng quát:**

Qua phân tích mối tương quan giữa **Tổng số video đăng tải** và các chỉ số **Lượt xem/Lượt thích/Lượt bình luận/Lượt chia sẻ trung bình trên mỗi video**, một xu hướng nhất quán đã được quan sát và có thể tổng quát hóa cho cả ba nhóm người dùng (Thấp, Trung bình, Cao về số người theo dõi):

1.  **Mối tương quan nghịch giữa Số lượng video và Tương tác trên mỗi video:**

    - Đối với tất cả các chỉ số tương tác được phân tích (Lượt xem, Lượt thích, Lượt bình luận, Lượt chia sẻ), đều tồn tại mối tương quan **nghịch** với tổng số lượng video đăng tải. Điều này có nghĩa là, nhìn chung, khi một TikToker đăng tải **càng nhiều video**, thì lượng tương tác trung bình (lượt xem, lượt thích, bình luận, chia sẻ) mà **mỗi video riêng lẻ** nhận được có xu hướng **giảm xuống**.
    - Mối tương quan nghịch này thể hiện rõ nhất ở **Lượt xem** và **Lượt thích**, và yếu dần ở **Lượt bình luận** và **Lượt chia sẻ**. Điều này cho thấy việc tăng số lượng video tác động mạnh hơn đến lượt xem và lượt thích trên từng video so với lượt bình luận và chia sẻ.
    - Đường xu hướng trên các biểu đồ phân tán đều minh họa xu hướng giảm của tương tác trên mỗi video khi số lượng video tăng lên.

2.  **Sự đánh đổi giữa Số lượng và Chất lượng (trên mỗi video):**
    - Kết quả này nhấn mạnh sự đánh đổi tiềm ẩn giữa số lượng và hiệu quả tương tác trên từng video. Mặc dù việc đăng nhiều video hơn có thể làm tăng tổng số lượt xem/tương tác kênh nhận được (do số lượng nội dung nhiều hơn), nó dường như lại làm "loãng" mức độ tương tác trung bình mà mỗi video đơn lẻ có thể thu hút.
    - Quan sát về các TikToker có **ít video nhưng đạt lượt tương tác trung bình trên mỗi video rất cao** (nằm ở góc trên bên trái của các biểu đồ phân tán) củng cố nhận định này. Những nhà sáng tạo này có thể đang tập trung vào việc sản xuất nội dung chất lượng cao, độc đáo, hoặc tìm được thị trường ngách hiệu quả, giúp tối đa hóa hiệu quả tương tác của từng video mà không cần đăng bài ồ ạt.

**Hàm ý cho Nhà sáng tạo nội dung (Tổng quát cho mọi nhóm):**

Dựa trên mối tương quan nghịch được quan sát, chiến lược "chất lượng hơn số lượng" (trên mỗi video) dường như là một yếu tố quan trọng để tối đa hóa mức độ tương tác trung bình cho từng nội dung.

- **Ưu tiên Chất lượng Nội dung:** Thay vì chỉ tập trung vào việc tăng tần suất đăng bài để có nhiều nội dung hơn, các nhà sáng tạo ở mọi nhóm (Thấp, Trung bình, Cao) nên ưu tiên đầu tư thời gian, công sức vào việc sản xuất các video có chất lượng cao, hấp dẫn, độc đáo và phù hợp với đối tượng mục tiêu.
- **Tối ưu hóa Tương tác trên từng Video:** Chú trọng vào các yếu tố giúp tăng tương tác trên mỗi video như nội dung giá trị, hình ảnh/âm thanh thu hút, kêu gọi hành động (call-to-action) rõ ràng, tương tác với bình luận của người xem, v.v..
- **Cân bằng giữa Số lượng và Chất lượng:** Nhà sáng tạo cần tìm ra sự cân bằng phù hợp giữa tần suất đăng bài đều đặn và việc duy trì chất lượng cho từng video để tối ưu hóa cả tổng tương tác kênh và hiệu quả của từng nội dung.

**Kết luận:**

Phân tích này cho thấy một xu hướng rõ ràng: việc tăng tổng số lượng video đăng tải có mối liên hệ tiêu cực với hiệu quả tương tác trung bình trên mỗi video. Điều này nhấn mạnh tầm quan trọng của chất lượng nội dung và chiến lược tối ưu hóa từng video đối với các nhà sáng tạo TikTok, bất kể họ đang ở mức độ người theo dõi nào.

## RQ: Sự khác biệt về thống kê trong 3 nhóm Follower

### 1. Số video mỗi tuần

1. Không có sự khác biệt có ý nghĩa thống kê: Giá trị p-value = 0.0856 lớn hơn mức ý nghĩa thông thường (0.05). Điều này có nghĩa là không có bằng chứng thống kê để kết luận rằng số lượng người theo dõi ảnh hưởng đáng kể đến số lượng video đăng tải mỗi tuần.

2. Xu hướng không rõ ràng: Mặc dù không có ý nghĩa thống kê, các giá trị trung bình cho thấy một xu hướng tăng nhẹ số video đăng tải mỗi tuần khi số lượng người theo dõi tăng lên (từ 4.41 ở nhóm Thấp đến 4.66 ở nhóm Cao). Tuy nhiên, sự khác biệt này là rất nhỏ và không đáng tin cậy.

3. Ý nghĩa cho nhà sáng tạo nội dung: Kết quả này gợi ý rằng, ít nhất dựa trên dữ liệu này, số lượng người theo dõi hiện tại không phải là yếu tố quyết định chính đến tần suất đăng video. Thay vào đó, các nhà sáng tạo có thể tập trung vào các yếu tố khác như chất lượng nội dung, thời điểm đăng bài, tương tác với người xem để tăng hiệu quả.

4. Chiến lược có thể rút ra:

   - Không tập trung quá mức vào việc tăng số lượng người theo dõi (chưa cần thiết): Trước mắt, các nhà sáng tạo có thể không cần quá lo lắng về việc tăng số lượng người theo dõi bằng mọi giá để tăng số video đăng tải.
   - Đa dạng hóa chiến lược nội dung: Cần tập trung vào việc tạo ra nội dung chất lượng, phù hợp với đối tượng mục tiêu, và tối ưu hóa các yếu tố khác ngoài số lượng người theo dõi, ví dụ như sử dụng các hashtag thịnh hành, tương tác tích cực với người xem, và thử nghiệm nhiều loại nội dung khác nhau để xem đâu là loại nội dung hiệu quả nhất.
   - Theo dõi và phân tích thêm: Cần tiếp tục theo dõi và phân tích dữ liệu để hiểu rõ hơn về mối quan hệ giữa các yếu tố khác (ví dụ: mức độ tương tác, loại nội dung) và tần suất đăng video.

### 2. Số hashtag trên mỗi video:

1. Sự khác biệt có ý nghĩa thống kê: Với p-value = 0.0000 (nhỏ hơn mức ý nghĩa thông thường là 0.05), kết quả kiểm định Kruskal-Wallis cho thấy có sự khác biệt có ý nghĩa thống kê về số lượng hashtag trên mỗi video giữa các nhóm người theo dõi (Thấp, Trung bình, Cao).

2. Nhóm có số hashtag cao nhất/thấp nhất: Dựa trên giá trị trung bình, nhóm người theo dõi Thấp có trung bình số hashtag trên mỗi video cao nhất (7.46), trong khi nhóm người theo dõi Cao có trung bình số hashtag trên mỗi video thấp nhất (5.73).

3. Ý nghĩa đối với nhà sáng tạo nội dung: Kết quả này cho thấy, những người có ít người theo dõi hơn có xu hướng sử dụng nhiều hashtag hơn trong video của họ. Điều này có thể là một nỗ lực để tăng khả năng hiển thị của video đến người xem mới, thông qua việc tận dụng các hashtag phổ biến hoặc liên quan. Ngược lại, những người có nhiều người theo dõi hơn có thể ít phụ thuộc vào hashtag vì họ đã có lượng khán giả ổn định.

4. Chiến lược rút ra:

   - Đối với người mới: Nên sử dụng một lượng hashtag vừa phải (ví dụ: trên 5 hashtag) để tăng cơ hội hiển thị video đến người xem mới. Việc nghiên cứu và sử dụng hashtag phù hợp với nội dung sẽ là yếu tố then chốt.
   - Đối với người có lượng người theo dõi lớn: Có thể giảm số lượng hashtag, tập trung vào nội dung chất lượng và tương tác với người xem.
   - Chiến lược chung: Các nhà sáng tạo nên theo dõi hiệu quả của hashtag (bằng cách xem xét mức độ tương tác và lượt xem) để điều chỉnh số lượng và loại hashtag sử dụng. Việc thử nghiệm và phân tích dữ liệu sẽ giúp tối ưu hóa chiến lược sử dụng hashtag.

### 3. Thời lượng video:

1. Có sự khác biệt có ý nghĩa thống kê: P-value = 0.0000 cho thấy có sự khác biệt đáng kể về thời lượng video giữa các nhóm người theo dõi (Thấp, Trung bình, Cao). Điều này có nghĩa là sự khác biệt về thời lượng video không chỉ là do ngẫu nhiên mà phản ánh mối liên hệ thực sự với số lượng người theo dõi.

2. Thời lượng video tăng theo số lượng người theo dõi: Nhóm người theo dõi Cao có thời lượng video trung bình cao nhất (103.56 giây), tiếp theo là nhóm Trung bình (74.48 giây) và cuối cùng là nhóm Thấp (59.01 giây).

3. Ý nghĩa đối với nhà sáng tạo nội dung: Kết quả này gợi ý rằng người dùng có nhiều người theo dõi có xu hướng tạo ra các video dài hơn. Điều này có thể liên quan đến nhiều yếu tố:

   - Sự đầu tư về nội dung: Các nhà sáng tạo có nhiều người theo dõi có thể đầu tư nhiều thời gian hơn vào việc sản xuất nội dung chất lượng cao, đòi hỏi thời lượng dài hơn để truyền tải.
   - Sự tương tác: Video dài hơn có thể cho phép họ xây dựng mối quan hệ sâu sắc hơn với khán giả và tăng cường sự tương tác.
   - Độ tin cậy và uy tín: Các video dài hơn có thể giúp người dùng chứng minh kiến thức, kỹ năng hoặc uy tín của họ trong lĩnh vực cụ thể.

4. Chiến lược có thể rút ra:

   - Nâng cao chất lượng nội dung: Những người sáng tạo có ít người theo dõi có thể tập trung vào việc cải thiện chất lượng nội dung của họ, dần dần tăng thời lượng video để thu hút và giữ chân người xem.
   - Thử nghiệm thời lượng: Cả người mới và người đã có lượng theo dõi nhất định nên thử nghiệm các độ dài video khác nhau để tìm ra thời lượng tối ưu phù hợp với nội dung và đối tượng mục tiêu.
   - Tập trung vào giá trị: Dù thời lượng là bao nhiêu, hãy đảm bảo video cung cấp giá trị thực tế, hữu ích và hấp dẫn để thu hút và duy trì sự quan tâm của người xem.

### Kết luận chung

**Kết quả phân tích chính:**

1.  **Về Số video đăng tải mỗi tuần:**

    - **Kết quả chính:** Phân tích cho thấy **không có sự khác biệt có ý nghĩa thống kê** về số lượng video đăng tải mỗi tuần giữa ba nhóm người dùng dựa trên số lượng người theo dõi (p-value = 0.0856 > 0.05).
    - **Nhận xét xu hướng:** Mặc dù giá trị trung bình có tăng nhẹ từ nhóm Thấp (4.41 video/tuần) lên nhóm Cao (4.66 video/tuần), sự khác biệt này không đủ lớn và đáng tin cậy để kết luận rằng số người theo dõi hiện tại là yếu tố quyết định chính đến tần suất đăng video.
    - **Ý nghĩa:** Kết quả này gợi ý rằng các nhà sáng tạo nội dung không nhất thiết phải tập trung vào việc tăng số lượng người theo dõi hiện tại để cải thiện tần suất đăng bài. Các yếu tố khác có thể đóng vai trò quan trọng hơn trong việc định hình thói quen đăng tải.

2.  **Về Số lượng hashtag trên mỗi video:**

    - **Kết quả chính:** Phân tích chỉ ra **có sự khác biệt có ý nghĩa thống kê** về số lượng hashtag trung bình trên mỗi video giữa các nhóm người dùng (p-value = 0.0000 < 0.05).
    - **Nhận xét xu hướng:** Nhóm người dùng có số lượng người theo dõi **Thấp** sử dụng trung bình số hashtag **cao nhất** (7.46 hashtag/video), trong khi nhóm **Cao** sử dụng số hashtag **thấp nhất** (5.73 hashtag/video).
    - **Ý nghĩa:** Xu hướng này có thể phản ánh chiến lược của người dùng. Những người có ít người theo dõi có xu hướng sử dụng nhiều hashtag hơn nhằm tăng khả năng khám phá video của họ bởi đối tượng khán giả mới. Ngược lại, những người đã có lượng người theo dõi lớn có thể ít phụ thuộc vào hashtag hơn.

3.  **Về Thời lượng video:**
    - **Kết quả chính:** Phân tích xác nhận **có sự khác biệt có ý nghĩa thống kê** về thời lượng video trung bình giữa ba nhóm người dùng theo số lượng người theo dõi (p-value = 0.0000 < 0.05).
    - **Nhận xét xu hướng:** Thời lượng video trung bình có xu hướng **tăng lên đáng kể** khi số lượng người theo dõi tăng. Nhóm Thấp có thời lượng trung bình ngắn nhất (59.01 giây), nhóm Trung bình dài hơn (74.48 giây), và nhóm Cao có thời lượng trung bình dài nhất (103.56 giây).
    - **Ý nghĩa:** Kết quả này ủng hộ quan sát rằng những người sáng tạo có lượng người theo dõi lớn hơn có xu hướng tạo ra các video có thời lượng dài hơn. Điều này có thể liên quan đến việc đầu tư nhiều hơn vào nội dung, khả năng giữ chân khán giả lâu hơn, hoặc xây dựng uy tín thông qua nội dung chuyên sâu hơn.

**Tóm tắt và Hàm ý:**

Kết quả phân tích cho thấy trong ba đặc điểm được khảo sát, **số lượng hashtag sử dụng** và **thời lượng video** có mối liên hệ có ý nghĩa thống kê với số lượng người theo dõi. Cụ thể, người dùng có ít người theo dõi có xu hướng dùng nhiều hashtag hơn và tạo video ngắn hơn, trong khi người dùng có nhiều người theo dõi lại dùng ít hashtag hơn và tạo video dài hơn. Ngược lại, **tần suất đăng tải video mỗi tuần** lại không cho thấy sự khác biệt đáng kể giữa các nhóm.

Đối với các nhà sáng tạo nội dung, những phát hiện này gợi ý rằng:

- Việc tăng tần suất đăng video có thể không trực tiếp phụ thuộc vào việc tăng số người theo dõi hiện có.
- Hashtag có thể là công cụ quan trọng hơn cho những người dùng mới hoặc có ít người theo dõi để tăng khả năng hiển thị.
- Thời lượng video có thể là một đặc điểm phát triển theo quá trình xây dựng lượng khán giả, khi người sáng tạo có thể đủ khả năng và lý do để tạo ra nội dung dài hơn và giữ chân người xem hiệu quả hơn.

# Trend Dashboard

## RQ: Miền nào (Bắc, Trung, Nam) là khu vực đóng góp số lượng video ẩm thực lớn nhất trên TikTok? Trong phạm vi mỗi miền, tỉnh/thành phố nào có sự đóng góp nhiều nhất về số lượng video?

**Tổng quan:**
Phân tích dữ liệu về xu hướng ẩm thực Việt Nam trên TikTok theo tiêu chí địa lý cho thấy sự tập trung đáng kể ở một số khu vực nhất định trong giai đoạn nghiên cứu.

**Kết quả chính:**

1.  **Tập trung ở các thành phố lớn:** Hà Nội và Thành phố Hồ Chí Minh là hai địa phương được đề cập/xuất hiện nhiều nhất trong tập dữ liệu, phản ánh vai trò trung tâm của hai đô thị này trong hoạt động sản xuất và tiêu thụ nội dung ẩm thực trên TikTok.
2.  **Phân bố theo 3 miền:** Khi phân chia theo ba miền địa lý chính, Miền Nam và Miền Bắc chiếm tỷ trọng đề cập vượt trội, với tổng cộng khoảng 93% số lượng video/đề cập. Miền Trung có số lượng đề cập thấp nhất.
3.  **Sự ảnh hưởng của thành phố trung tâm trong mỗi miền:** Tỷ lệ đề cập trong mỗi miền (Bắc và Nam) bị chi phối mạnh mẽ bởi thành phố trung tâm của miền đó. Cụ thể, Hà Nội đóng góp tới 85% số đề cập trong Miền Bắc và Thành phố Hồ Chí Minh đóng góp tới 85% số đề cập trong Miền Nam.
4.  **Đặc điểm của Miền Trung:** Trái ngược với Miền Bắc và Miền Nam, số lượng đề cập đến các tỉnh thành trong Miền Trung có sự phân bố đồng đều hơn giữa các địa phương, không quá phụ thuộc vào một vài thành phố dẫn đầu. Các địa phương xuất hiện nhiều nhất tại Miền Trung chủ yếu là các thành phố du lịch trọng điểm như Đà Lạt, Nha Trang, Huế, Đà Nẵng.

**Nhận xét và Hàm ý Chiến lược:**

Sự phân bố địa lý này gợi ý rằng trong khi Hà Nội và Thành phố Hồ Chí Minh là những trung tâm nội dung ẩm thực lớn và sầm uất, chúng cũng đồng thời là những thị trường có độ cạnh tranh rất cao.

Đối với các nhà sáng tạo nội dung, dữ liệu cho thấy một hướng đi tiềm năng: thay vì cố gắng cạnh tranh trực tiếp trong những thị trường đã bão hòa như Hà Nội và TP. Hồ Chí Minh, việc tập trung khai thác các **thị trường ngách tại các thành phố du lịch** (đặc biệt là ở Miền Trung) có thể là chiến lược hiệu quả. Tại những địa điểm này, sự cạnh tranh có thể ít gay gắt hơn, và nhà sáng tạo có cơ hội xây dựng một tệp người xem/khán giả riêng, quan tâm đến ẩm thực đặc trưng hoặc trải nghiệm ăn uống tại các điểm du lịch.
