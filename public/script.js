// public/script.js (비동기 방식 최종 버전)

// Firebase 초기화 코드는 index.html에 이미 있어야 합니다.
// const firebaseConfig = { ... };
// firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// HTML 요소 가져오기
const musicForm = document.getElementById('musicForm'); // HTML의 form id를 'musicForm'으로 맞춰주세요
const promptInput = document.getElementById('prompt'); // HTML의 input id를 'prompt'로 맞춰주세요
const resultDiv = document.getElementById('result'); // HTML의 결과 표시 div id를 'result'로 맞춰주세요
const spinner = document.getElementById('spinner'); // HTML의 스피너 div id를 'spinner'로 맞춰주세요

// Firestore 리스너를 해제하기 위한 변수
let unsubscribe; 

musicForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = promptInput.value;
    if (!prompt) {
        alert('음악에 대한 설명을 입력해주세요.');
        return;
    }

    // UI를 '로딩 중' 상태로 변경
    spinner.style.display = 'block';
    resultDiv.innerHTML = '주문을 접수하는 중입니다... 🚀';
    promptInput.disabled = true;
    document.querySelector('button').disabled = true;

    // 이전에 실행 중이던 리스너가 있다면, 먼저 해제
    if (unsubscribe) {
        unsubscribe();
    }

    try {
        // 1. '/generate_music' 함수를 호출합니다. (상대 경로 사용)
        // Firebase Hosting이 알아서 올바른 함수로 연결해줍니다.
        const response = await fetch('/generate_music', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`주문 접수 실패: ${errorText}`);
        }

        const data = await response.json();
        const { document_id } = data; // 백엔드로부터 '주문서 ID'를 받습니다.

        // 2. 사용자에게 주문 접수를 알리고, 결과 리스닝을 시작
        resultDiv.innerHTML = `주문 접수 완료! (주문 ID: ${document_id})<br>AI가 음악을 만드는 중입니다. 잠시만 기다려 주세요... 🎶`;
        
        // 3. Firestore 문서에 대한 실시간 리스너를 시작합니다!
        listenForMusicResult(document_id);

    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `오류가 발생했습니다: ${error.message}`;
        spinner.style.display = 'none';
        promptInput.disabled = false;
        document.querySelector('button').disabled = false;
    }
});

function listenForMusicResult(docId) {
    const docRef = db.collection('music_requests').doc(docId);

    // onSnapshot: 해당 문서에 변경이 생길 때마다 자동으로 아래 함수를 실행합니다.
    unsubscribe = docRef.onSnapshot((doc) => {
        if (!doc.exists) {
            console.error("해당 문서를 찾을 수 없습니다!");
            return;
        }

        const data = doc.data();

        // 4. 문서의 'status' 필드를 확인하고 UI를 업데이트
        if (data.status === 'completed') {
            spinner.style.display = 'none';
            resultDiv.innerHTML = `<h3>음악 생성 완료!</h3>
                                 <p><strong>프롬프트:</strong> ${data.prompt}</p>
                                 <audio controls src="${data.output_url}">
                                     오디오를 지원하지 않는 브라우저입니다.
                                 </audio>`;
            
            promptInput.disabled = false;
            document.querySelector('button').disabled = false;
            unsubscribe(); 

        } else if (data.status === 'failed') {
            spinner.style.display = 'none';
            resultDiv.innerHTML = `<p class="error">생성에 실패했습니다. 😭</p>
                                 <p><strong>오류:</strong> ${data.error || '알 수 없는 오류'}</p>`;
            promptInput.disabled = false;
            document.querySelector('button').disabled = false;
            unsubscribe();
        } 
        
    }, (error) => {
        console.error("실시간 리스닝 오류: ", error);
        resultDiv.innerHTML = `결과를 기다리는 중 오류 발생: ${error.message}`;
        spinner.style.display = 'none';
        promptInput.disabled = false;
        document.querySelector('button').disabled = false;
    });
}