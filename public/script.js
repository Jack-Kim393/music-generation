// public/script.js (최종 완성 버전)

// HTML에 있는 각 요소들을 변수에 담아둡니다.
const musicForm = document.getElementById('music-form');
const promptInput = document.getElementById('prompt-input');
const resultContainer = document.getElementById('result-container');
const loadingIndicator = document.getElementById('loading');
const generateButton = musicForm.querySelector('button');

// '음악 생성' 폼이 제출되었을 때의 동작을 정의합니다.
musicForm.addEventListener('submit', async (event) => {
    // 1. form의 기본 동작(페이지 새로고침)을 막습니다.
    event.preventDefault();

    // 2. 사용자가 입력한 프롬프트 값을 가져옵니다.
    const prompt = promptInput.value;

    // 3. UI를 '로딩 중' 상태로 변경합니다.
    resultContainer.innerHTML = ''; // 이전 결과 삭제
    loadingIndicator.style.display = 'block'; // 로딩 스피너 보여주기
    generateButton.disabled = true; // 버튼 비활성화
    generateButton.textContent = '생성 중...';

    // 4. 우리의 실제 클라우드 함수 URL로 요청을 보냅니다.
    const functionUrl = 'https://generate-music-yf6l5gdmia-uc.a.run.app';

    try {
        // 5. API 서버에 fetch를 이용해 요청을 보냅니다.
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

        // 6. 서버로부터 받은 응답을 처리합니다.
        if (response.ok) { // 응답이 성공적일 경우 (status code 200-299)
            const result = await response.json();
            if (result.success && result.music_url) {
                // 성공적으로 음악 URL을 받으면, 오디오 플레이어를 생성합니다.
                const audioPlayer = `<audio controls autoplay src="${result.music_url}"></audio>`;
                resultContainer.innerHTML = audioPlayer;
            } else {
                // 성공은 했지만, 데이터에 문제가 있을 경우
                resultContainer.innerHTML = `<p class="error">오류 발생: ${result.error || 'API 서버에서 음악 생성에 실패했습니다.'}</p>`;
            }
        } else { // 응답이 실패일 경우 (status code 4xx, 5xx)
            resultContainer.innerHTML = `<p class="error">서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>`;
        }

    } catch (error) {
        // 네트워크 문제 등 fetch 요청 자체가 실패한 경우
        resultContainer.innerHTML = `<p class="error">요청 중 심각한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>`;
        console.error('Error:', error);
    } finally {
        // 7. 성공하든 실패하든, 모든 과정이 끝나면 UI를 다시 원래 상태로 되돌립니다.
        loadingIndicator.style.display = 'none'; // 로딩 스피너 숨기기
        generateButton.disabled = false; // 버튼 다시 활성화
        generateButton.textContent = '음악 생성';
    }
});