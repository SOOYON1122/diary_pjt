from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages

from .models import Diary, Note, NoteImage, Comment
from friends.models import Friendship
from .forms import DiaryForm, NoteForm, CommentForm, NoteImageFormSet

User = get_user_model()

# ================= 다이어리 영역 =================

# 최초 사이트 진입 시 보이는 메인화면
def index(request):
  return render(request, 'diaries/index.html')


# 다이어리 생성
def creatediary(request):
  if request.method == 'POST':
    form = DiaryForm(request.POST, request.FILES, user=request.user)
    if form.is_valid():
      diary = form.save(commit=False)
      diary.user = request.user
      diary.save()

      # 친구 목록 저장
      friends = request.POST.get('diary_friends', '') # 리스트로 가져오기
      print("친구 ID들:", friends)  # 디버깅 출력
      
      if friends:  # 리스트가 비어있지 않으면
        # friends를 정수형 리스트로 변환
        friends_ids = [int(friend) for friend in friends.split(',') if friend.isdigit()]
        print("정수형 친구 ID들:", friends_ids)  # 디버깅 출력
        
        # 친구를 추가
        diary.diary_friends.set(friends_ids)  
        print("친구 목록이 성공적으로 추가되었습니다.")  # 디버깅 출력
      else:
        print("친구 ID가 비어 있습니다.")  # 디버깅 출력

      return redirect('diaries:my_diary')
    
  else:
    form = DiaryForm(user=request.user)

  # 친구 목록 가져오기
  friends_queryset = Friendship.objects.filter(
      Q(from_user=request.user) | Q(to_user=request.user),
      is_friend=True
  ).values_list('from_user', 'to_user', flat=False)

  # 친구 아이디들만 리스트로 추출
  friend_ids = set()
  for from_user, to_user in friends_queryset:
    if from_user == request.user.id:
      friend_ids.add(to_user)
    else:
      friend_ids.add(from_user)

  # User 모델을 통해 친구를 필터링합니다.
  friends = User.objects.filter(id__in=friend_ids)

  context = {
    'form': form,
    'friends': friends,  # 친구 목록 전달
  }
  return render(request, 'diaries/creatediary.html', context)


# 내 다이어리 목록
def mydiary(request):
  # 내가 주인인 다이어리
  owner_diaries = Diary.objects.filter(user=request.user)
  # 내가 친구로 참여중인 다이어리
  member_diaries = Diary.objects.filter(diary_friends=request.user)

  context = {
    'owner_diaries': owner_diaries,
    'member_diaries': member_diaries,
  }
  
  return render(request, 'diaries/mydiary.html', context)



# ================= 노트영역 =================

@login_required
def notelist(request, diary_pk):
    diary = get_object_or_404(Diary, pk=diary_pk)
    notes = Note.objects.filter(diary=diary)  # 해당 다이어리에 속한 모든 노트 가져오기

    paginator = Paginator(notes, 10)  # 페이지당 10개의 노트
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'diary': diary,
        'page_obj': page_obj,
    }
    return render(request, 'diaries/note_list.html', context)

@login_required
def notedetail(request, diary_pk, note_pk):
    diary = get_object_or_404(Diary, pk=diary_pk)
    comment_form = CommentForm()
    note = get_object_or_404(Note, pk=note_pk, diary=diary)
    note_images = NoteImage.objects.filter(note=note)  # 해당 노트에 속한 이미지 가져오기
    

    context = {
        'diary': diary,
        'note': note,
        'note_images': note_images,
        'comment_form': comment_form,
    }
    return render(request, 'diaries/notedetail.html', context)

@login_required
def createnote(request, diary_pk):
    diary = get_object_or_404(Diary, pk=diary_pk)
    
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        formset = NoteImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            # if not form.is_valid():
            #     print(form.errors)  # 디버깅용 출력
            # if not formset.is_valid():
            #     print(formset.errors)  # 디버깅용 출력
            note = form.save(commit=False)
            note.diary_id = diary.id
            note.user_id = request.user.id
            note.save()  # Note 객체를 먼저 저장합니다.

            formset.instance = note
            
            for note_image_form in formset:
                if note_image_form.cleaned_data.get('image'):  # 이미지가 비어있지 않은 경우에만 저장
                    note_image_instance = note_image_form.save(commit=False)  # 커밋하지 않고 인스턴스 생성
                    note_image_instance.user = request.user  # 사용자 설정
                    note_image_instance.note = note  # 방금 저장한 노트와 연결
                    note_image_instance.save()  # 저장

            messages.success(request, "노트가 성공적으로 생성되었습니다.")
            return redirect('diaries:note_detail', diary_pk=diary.pk, note_pk=note.pk)
        else:
            messages.error(request, "노트 작성 중 오류가 발생했습니다. 다시 시도해주세요.")
    else:
        form = NoteForm()
        formset = NoteImageFormSet()

    context = {
        'form': form,
        'formset': formset,
        'diary': diary,
    }
    return render(request, 'diaries/createnote.html', context)

@login_required
def delete_note(request, diary_pk, note_pk):
    note = get_object_or_404(Note, pk=note_pk)

    if request.user == note.user:
        note.delete()
        messages.success(request, "노트가 삭제되었습니다.") 
    else:
        messages.error(request, "권한이 없습니다. 이 노트를 삭제할 수 없습니다.")

    return redirect('diaries:note_list', diary_pk)


@login_required
def editnote(request, diary_pk, note_pk):
    diary = get_object_or_404(Diary, pk=diary_pk)
    note = get_object_or_404(Note, pk=note_pk)

    # NoteImageFormSet을 노트 이미지 인스턴스로 초기화합니다.
    formset = NoteImageFormSet(queryset=note.note_images.all())  # 'note_images'는 related_name입니다.

    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        formset = NoteImageFormSet(request.POST, request.FILES, instance=note)

        if form.is_valid() and formset.is_valid():
            note = form.save(commit=False)
            note.save(update_fields=form.cleaned_data.keys())  # 변경된 필드만 저장
            
            # 이미지 처리
            for note_image_form in formset:
                if note_image_form.cleaned_data.get('image'):
                    note_image_instance = note_image_form.save(commit=False)
                    note_image_instance.note = note
                    note_image_instance.user = request.user
                    note_image_instance.save()
                elif note_image_form.instance.pk:  # 기존 이미지가 있는 경우
                    note_image_form.instance.note = note
                    note_image_form.instance.user = request.user
                    note_image_form.instance.save()

            # messages.success(request, "노트가 성공적으로 수정되었습니다.")
            return redirect('diaries:note_detail', diary_pk=diary.pk, note_pk=note.pk)
        else:
            print(form.errors)  # 디버깅용: 폼 에러 출력
            print(formset.errors)  # 디버깅용: 이미지 폼셋 에러 출력
            messages.error(request, "폼에 오류가 있습니다. 다시 시도해주세요.")
    else:
        form = NoteForm(instance=note)

    context = {
        'form': form,
        'formset': formset,
        'diary': diary,
        'note': note,
    }
    return render(request, 'diaries/editnote.html', context)


@login_required
def comments_create(request, diary_pk, note_pk):
    diary = get_object_or_404(Diary, pk=diary_pk)
    note = get_object_or_404(Note, pk=note_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.note = note
            comment.user = request.user
            comment.save()
        return redirect('diaries:note_detail', diary_pk=diary_pk, note_pk=note_pk)

    return redirect('diaries:note_detail', diary_pk=diary_pk, note_pk=note_pk)

@login_required
def comments_delete(request, diary_pk, note_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:  # 사용자가 댓글 작성자인지 확인
        comment.delete()
    return redirect('diaries:note_detail', diary_pk=diary_pk, note_pk=note_pk)

def likes(request, diary_pk, note_pk):
    if request.method == "POST":
        diary = get_object_or_404(Diary, pk=diary_pk)
        note = get_object_or_404(Note, pk=note_pk)
        if request.user in note.like_users.all():
            note.like_users.remove(request.user)
        else:
            note.like_users.add(request.user)

        return redirect('diaries:note_detail', diary_pk=diary_pk, note_pk=note_pk)
    return redirect('diaries:note_detail', diary_pk=diary_pk, note_pk=note_pk)