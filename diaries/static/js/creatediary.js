document.addEventListener('DOMContentLoaded', function() {
  const friendSelect = document.getElementById('friend-select');
  const selectedFriendsDiv = document.getElementById('selected-friends');

  friendSelect.addEventListener('change', function() {
    // 선택된 옵션을 배열로 변환
    const selectedOptions = Array.from(friendSelect.selectedOptions);

    // 선택된 친구들의 이름을 화면에 출력
    selectedFriendsDiv.innerHTML = '';  // 기존 내용을 비워줌
    selectedOptions.forEach(option => {
      const friendName = option.text;
      const friendParagraph = document.createElement('p');
      friendParagraph.textContent = friendName;
      selectedFriendsDiv.appendChild(friendParagraph);
    });

    // 최대 7명 제한
    if (selectedOptions.length > 7) {
      alert('친구는 최대 7명까지 선택할 수 있습니다.');
      // 마지막 선택된 친구를 선택 해제
      option.selected = false;
    }
  });
});
