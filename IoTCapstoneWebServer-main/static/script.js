document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('table');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    let currentDate = new Date();
    let csvFileName = getCurrentCSVFileName(); // 현재 CSV 파일 이름을 가져오는 함수를 호출하여 초기화
    let currentPage = 0;
    let rowsPerPage = 30;

    // CSV 파일 이름을 현재 날짜의 포맷에 맞게 반환하는 함수
    function getCurrentCSVFileName() {
        const dateFormat = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
        return `static/data/${dateFormat}.csv`;
    }

    // 테이블 초기화 함수
    function clearTable() {
        const tbody = document.querySelector('#table tbody');
        tbody.innerHTML = '';
    }

    // CSV 파일에서 데이터를 읽어와서 HTML 테이블에 추가하는 함수
    function loadCSVData() {
        // 테이블 초기화
        clearTable();

        // 캐시 방지를 위한 쿼리 파라미터 추가
        const cacheBuster = new Date().getTime();
        fetch(`${csvFileName}?cacheBuster=${cacheBuster}`)
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('File not found');
                } else {
                    throw new Error('Network response was not ok');
                }
            }
            showTableDate();
            return response.text();
        })
        .then(data => {
            const rows = data.split('\n');
            rowsPerPage = rows.length;
            const startIndex = currentPage * rowsPerPage;
            const endIndex = startIndex + rowsPerPage;
            const slicedRows = rows.slice(startIndex, endIndex);
            const tbody = document.querySelector('#table tbody');
            //csv 없을 시 데이터가 없다는 메시지 출력
            if (slicedRows.length === 0) {
                const tr = document.createElement('tr');
                const td = document.createElement('td');
                td.textContent = '저장된 데이터가 없습니다';
                td.colSpan = 2;
                tr.appendChild(td);
                tbody.appendChild(tr);
            } else {
                slicedRows.forEach(row => {
                    const cells = row.split(',');
                    const tr = document.createElement('tr');
                    cells.forEach((cell, index) => {
                        const td = document.createElement('td');
                        const lowerCaseCell = cell.trim().toLowerCase();
                        if (index === 0 && (lowerCaseCell.endsWith('.jpg') || lowerCaseCell.endsWith('.png'))) { //테이블 첫 번째 열에 이미지 표시
                            const img = document.createElement('img');
                            img.src = `static/pics/${cell.trim()}`;
                            img.width = 720;
                            img.height = 480;
                            td.appendChild(img);
                        } else {
                            td.textContent = cell.trim(); //두 번째 열에 위반 시간 표시
                        }
                        tr.appendChild(td);
                    });

                    tbody.appendChild(tr);
                });
            }
        })
        .catch(error => {
            console.error('Error loading CSV file:', error);
            // CSV 파일이 없을 경우, 데이터가 없다는 메시지 출력
            if (error.message === 'File not found') {
                showTableDate();
                const tbody = document.querySelector('#table tbody');
                tbody.innerHTML = '';
                const tr = document.createElement('tr');
                const td = document.createElement('td');
                td.textContent = '저장된 데이터가 없습니다';
                td.colSpan = 2;
                tr.appendChild(td);
                tbody.appendChild(tr);
            }
        });
    }

    function showTableDate() {
        const tableDate = document.getElementById('table_date');
        tableDate.textContent = `${currentDate.getFullYear()}년 ${(currentDate.getMonth() + 1).toString().padStart(2, '0')}월 ${currentDate.getDate().toString().padStart(2, '0')}일` + " 신호위반 차량 목록";
    }

    // 현재 시간을 표시하는 함수
    function updateTime() {
        const currentTime = new Date();
        const year = currentTime.getFullYear();
        const month = (currentTime.getMonth() + 1).toString().padStart(2, '0');
        const day = currentTime.getDate().toString().padStart(2, '0');
        const hours = currentTime.getHours().toString().padStart(2, '0');
        const minutes = currentTime.getMinutes().toString().padStart(2, '0');
        const seconds = currentTime.getSeconds().toString().padStart(2, '0');
        const formattedTime = `${year}년 ${month}월 ${day}일 ${hours}시 ${minutes}분 ${seconds}초`;

        const currentTimeElement = document.getElementById('date');
        currentTimeElement.textContent = "현재 시간: " + formattedTime;
    }

    prevButton.addEventListener('click', function() {
        currentPage = Math.max(0, currentPage - 1);
        updateDate(-1);
        loadCSVData();
    });

    nextButton.addEventListener('click', function() {
        currentPage = Math.min(Math.floor(table.rows.length / rowsPerPage), currentPage + 1);
        updateDate(1);
        loadCSVData();
    });

    function updateDate(diff) {
        currentDate.setDate(currentDate.getDate() + diff);
        csvFileName = getCurrentCSVFileName(); // CSV 파일 이름을 업데이트
    }

    // 초기화
    loadCSVData();
    updateTime();
    setInterval(updateTime, 1000);

    // 1분마다 CSV 데이터를 다시 로드
    setInterval(loadCSVData, 60000);
});