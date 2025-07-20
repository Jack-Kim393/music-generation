// HTML 요소들을 가져옵니다.
const musicForm = document.getElementById('music-form');
const promptInput = document.getElementById('prompt-input');
const resultContainer = document.getElementById('result-container');
const loadingIndicator = document.getElementById('loading');
const generateButton = musicForm.querySelector('button');

// 폼 제출(submit) 이벤트가 발생했을 때 실행할 함수를 정의합니다.
musicForm.addEventListener('submit', async (event) => {
    // 1. 폼의 기본 동작(페이지 새로고침)을 막습니다.
    event.preventDefault();

    // 2. 입력된 프롬프트 값을 가져옵니다.
    const prompt = promptInput.value;

    // 3. 이전 결과는 지우고, 로딩 상태를 보여주고, 버튼을 비활성화합니다.
    resultContainer.innerHTML = '';
    loadingIndicator.style.display = 'block';
    generateButton.disabled = true;
    generateButton.textContent = '생성 중...';

    // 4. Firebase Function의 실제 URL로 POST 요청을 보냅니다.
    const functionUrl = 'https://generate-music-yf6l5gdmia-uc.a.run.app';

    try {
        const response = await fetch(functionUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: {
                    prompt: prompt
                }
            })
        });

        // 5. 함수로부터 받은 응답을 처리합니다.
        if (response.ok) {
            // 성공 응답 (200 OK)을 받으면 오디오 플레이어를 생성합니다.
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audioPlayer = `<audio controls autoplay src="${audioUrl}"></audio>`;
            resultContainer.innerHTML = audioPlayer;
        } else {
            // 실패 응답을 받으면 에러 메시지를 표시합니다.
            const errorResult = await response.json();
            resultContainer.innerHTML = `<p class="error">오류 발생: ${errorResult.error || '알 수 없는 오류'}</p>`;
        }

    } catch (error) {
        // 네트워크 에러 등 fetch 자체에 문제가 생긴 경우
        resultContainer.innerHTML = `<p class="error">요청 중 심각한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>`;
        console.error('Error:', error);
    } finally {
        // 6. 모든 작업이 끝나면 로딩 상태를 숨기고, 버튼을 다시 활성화합니다.
        loadingIndicator.style.display = 'none';
        generateButton.disabled = false;
        generateButton.textContent = '음악 생성';
    }
});