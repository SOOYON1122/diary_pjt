function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function deleteFriendConfirm(friend_id, friend_name){
  const isConfirmed = confirm(`정말 ${friend_name} 친구를 삭제하시겠어요?`);

  if (isConfirmed) {
    $.ajax({
      url: `/friends/delete-friend/${friend_id}/`,
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ friend_id: friend_id }),
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      success: function(data) {
        alert('친구가 삭제되었습니다!');
        location.reload();  // 페이지 리로드로 변경 사항 반영
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.error('문제가 발생했습니다:', textStatus, errorThrown);
        alert('친구 삭제에 실패했습니다.');
      }
    });
  }
}
