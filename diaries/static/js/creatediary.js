document.addEventListener('DOMContentLoaded', function() {
  const friendListItems = document.querySelectorAll('.friend-item');
  const selectedFriendIdsInput = document.getElementById('selected-friend-ids');
  const selectedFriendsDiv = document.getElementById('selected-friends');

  friendListItems.forEach(item => {
    item.addEventListener('click', function() {
      const friendId = item.dataset.id;

      // 친구 ID가 이미 선택된 경우
      if (selectedFriendIdsInput.value.includes(friendId)) {
        // 선택 해제
        selectedFriendIdsInput.value = selectedFriendIdsInput.value
          .split(',')
          .filter(id => id !== friendId)
          .join(',');
        item.classList.remove('selected'); // 선택 상태 변경
      } else {
        // 선택 추가
        selectedFriendIdsInput.value += selectedFriendIdsInput.value ? ',' + friendId : friendId;
        item.classList.add('selected'); // 선택 상태 변경
      }

      // 선택된 친구의 이름을 화면에 출력
      updateSelectedFriendsDisplay();
    });
  });

  function updateSelectedFriendsDisplay() {
    selectedFriendsDiv.innerHTML = ''; // 기존 내용을 비워줌
    const selectedIds = selectedFriendIdsInput.value.split(',');

    selectedIds.forEach(id => {
      if (id) {
        const friendItem = Array.from(friendListItems).find(item => item.dataset.id === id);
        if (friendItem) {
          const friendName = friendItem.textContent; // username과 nickname을 사용
          const friendParagraph = document.createElement('p');
          friendParagraph.textContent = friendName;
          selectedFriendsDiv.appendChild(friendParagraph);
        }
      }
    });
  }
});
