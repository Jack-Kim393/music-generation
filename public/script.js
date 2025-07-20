// public/script.js

// ... (파일 상단의 const 변수 선언은 그대로 둡니다) ...

musicForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const prompt = promptInput.value;

    resultContainer.innerHTML = '';
    loadingIndicator.style.display = 'block';
    generateButton.disabled = true;
    generateButton.textContent = '주문 접수 중...'; // 버튼 텍스트 변경

    const functionUrl = 'https://generate-music-yf6l5gdmia-uc.a.run.app';

    try {
        const response = await fetch(functionUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: { prompt: prompt } })
        });

        const result = await response.json();

        if (result.success) {
            // 성공 시, 음악 URL 대신 '주문 번호표(jobId)'를 화면에 표시합니다.
            resultContainer.innerHTML = `<p>주문이 성공적으로 접수되었습니다!<br>작업 ID: ${result.jobId}</p><p>이제 곧 음악 생성이 시작됩니다...</p>`;
        } else {
            resultContainer.innerHTML = `<p class="error">오류 발생: ${result.error}</p>`;
        }

    } catch (error) {
        resultContainer.innerHTML = `<p class="error">요청 중 심각한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>`;
        console.error('Error:', error);
    } finally {
        // 성공하든 실패하든 로딩을 숨기고 버튼을 다시 활성화합니다.
        loadingIndicator.style.display = 'none';
        generateButton.disabled = false;
        generateButton.textContent = '음악 생성';
    }
});