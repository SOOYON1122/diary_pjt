from django.shortcuts import render, redirect
from .forms import FriendshipForm
from .models import Friendship
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
User = get_user_model()

# 친구 검색하기 (친구추가용)
def searchfriend(request):
  
  query = request.GET.get('q', '').strip()
  category = request.GET.get('category', 'username').strip()
  results = []

  if query:
    # 현재 사용자와 이미 친구인 사용자 ID를 가져옴
    friend_ids = Friendship.objects.filter(
      Q(from_user_id=request.user.id) | Q(to_user_id=request.user.id), 
      is_friend=True
    ).values_list('from_user_id', 'to_user_id')
    friend_ids = set()  # 빈 세트 초기화
    for from_id, to_id in friend_ids:
      friend_ids.add(from_id)
      friend_ids.add(to_id)
    if category == 'username':
      users = User.objects.exclude(id__in=friend_ids).filter(username__icontains=query)
      results = [{'id': user.id, 'display_name': user.username} for user in users]
    elif category == 'email':
      users = User.objects.exclude(id__in=friend_ids).filter(email__icontains=query)
      results = [{'id': user.id, 'display_name': user.email} for user in users]

  return JsonResponse({'results': results})


# 친구추가 로직
@login_required
def addfriend(request):
  if request.method == 'POST':
    to_user_id = request.POST.get('to_user')

    # 만약 카테고리가 이메일일 경우 유저의 아이디로 치환
    if request.POST.get('category') == 'email':
      try:
        to_user = User.objects.get(email=to_user_id)
        to_user_id = to_user.id
      except User.DoesNotExist:
        messages.error(request, '존재하지 않는 이메일입니다.')
        return redirect('friends:add_friend')

    # 친구목록에 존재하지 않는다면 친구신청
    if not Friendship.objects.filter(from_user_id=request.user.id, to_user_id=to_user_id).exists() and \
       not Friendship.objects.filter(from_user_id=to_user_id, to_user_id=request.user.id).exists():

      Friendship.objects.create(from_user_id=request.user.id, to_user_id=to_user_id, is_friend=False)
      messages.success(request, '친구 신청이 완료되었습니다!')
      return redirect('diaries:index')

    # 이미 친구신청을 보낸 유저라면 빠꾸
    elif Friendship.objects.filter(from_user_id=request.user.id, to_user_id=to_user_id, is_friend=False).exists():
      messages.error(request, '이미 친구신청을 보냈습니다.')
      return redirect('friends:add_friend')

    # 상대가 이미 친구신청을 한 상태라면 친구수락
    friend_query = Friendship.objects.filter(from_user_id=to_user_id, to_user_id=request.user.id, is_friend=False)
    if friend_query.exists():
      friend = friend_query.first()  # 존재할 경우 첫 번째 객체 가져오기
      friend.is_friend = True
      friend.save()
      messages.success(request, '기존 친구신청 요청이 확인되어 서로 친구가 되었습니다.')
      return redirect('diaries:index')

    # 그외 유저가 없거나 입력값이 틀린 경우
    messages.error(request, '존재하지 않는 유저이거나 입력값이 잘못되었습니다.')
    return redirect('friends:add_friend')

  else:
    form = FriendshipForm()

  context = {
    'form': form,
  }

  return render(request, 'friends/addfriend.html', context)
    

# 내 친구 목록
@login_required
def myfriends(request):
  waitfriends = Friendship.objects.filter(to_user_id=request.user.id, is_friend=False).select_related('from_user')
  myrequests = waitfriends = Friendship.objects.filter(from_user_id=request.user.id, is_friend=False).select_related('to_user')
  friends = Friendship.objects.filter(
    Q(to_user_id=request.user.id, is_friend=True) | Q(from_user_id=request.user.id, is_friend=True)
  ).select_related('from_user')

  if waitfriends.exists():
    messages.success(request, f'{waitfriends.count()}개의 미확인 친구신청이 있습니다!')

  
  context = {
    'waitfriends': waitfriends,
    'friends': friends,
    'myrequests': myrequests,
  }
  return render(request, 'friends/myfriends.html', context)


# 친구 수락 로직
def acceptfriend(request, friend_id):
  if request.method == 'POST':
    try:
      friend_request = Friendship.objects.get(from_user_id=friend_id, to_user_id=request.user.id, is_friend=False)
      friend_request.is_friend = True
      friend_request.save()
      messages.success(request, '친구 신청을 수락했습니다.')
    except Friendship.DoesNotExist:
      messages.error(request, '친구 신청이 존재하지 않거나 이미 수락되었습니다.')
    return redirect('friends:my_friends')
  return redirect('friends:my_friends')


# 친구 거절 로직
def rejectfriend(request, friend_id):
  if request.method == 'POST':
    try:
      friend_request = Friendship.objects.get(from_user_id=friend_id, to_user_id=request.user.id, is_friend=False)
      friend_request.delete()
      messages.success(request, '친구 신청을 거절했습니다.')
    except Friendship.DoesNotExist:
      messages.error(request, '친구 신청이 존재하지 않습니다.')
    return redirect('friends:my_friends')
  return redirect('friends:my_friends')


# 친구신청 취소 로직
def cancelfriend(request, friend_id):
  if request.method == 'POST':
    try:
      friend_request = Friendship.objects.get(from_user_id=request.user.id, to_user_id=friend_id, is_friend=False)
      friend_request.delete()
      messages.success(request, '친구 신청을 취소했습니다.')
    except Friendship.DoesNotExist:
      messages.error(request, '친구 신청이 존재하지 않습니다.')
    return redirect('friends:my_friends')
  return redirect('friends:my_friends')


# 친구 삭제 로직
def deletefriend(request, friend_id):
  if request.method == 'POST':
    try:
      friendship = Friendship.objects.get(
        Q(from_user_id=request.user.id, to_user_id=friend_id, is_friend=True) |
        Q(from_user_id=friend_id, to_user_id=request.user.id, is_friend=True)
      )
      friendship.delete()
      messages.success(request, '친구를 삭제했습니다.')
    except Friendship.DoesNotExist:
      messages.error(request, '친구가 존재하지 않습니다.')
    return redirect('friends:my_friends')
  return redirect('friends:my_friends')
