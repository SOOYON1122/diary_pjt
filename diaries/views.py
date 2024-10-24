from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Diary, Note, NoteImage, Comment
from .forms import DiaryForm, NoteForm, NoteImageForm, CommentForm



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
      friends = request.POST.getlist('diary_friends')
      diary.diary_friends.set(friends)

      return redirect('diaries:my_diary', diary.id)
  else:
    form = DiaryForm(user=request.user)

  context = {
    'form': form,
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
def noteindex(request, diary_pk):
    diary = Diary.objects.get(pk=diary_pk)
    date_filter = request.GET.get('date')
    if date_filter:
        notes = Note.objects.filter(created_at__date=date_filter)
    else:
        notes = Note.objects.all()

    paginator = Paginator(notes, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comment_form = CommentForm()
    context = {
        'page_obj' : page_obj,
        'comment_form': comment_form,
        'diary': diary,
    }
    return render(request, 'diaries/noteindex.html', context)


def notedetail(request, diary_pk, note_pk):
    pass

@login_required
def createnote(request, diary_pk):
    diary = Diary.objects.get(pk=diary_pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        
        if form.is_valid():
            note = form.save(commit=False)
            note.diary_id = diary_pk  # diary_pk를 사용하여 note에 설정
            note.user = request.user  # user를 올바르게 설정
            note.save()

            images = request.FILES.getlist('image')
            if len(images) > 10:
                form.add_error(None, "이미지는 최대 10개까지만 업로드할 수 있습니다.")
            else:
                for image in images:
                    NoteImage.objects.create(note=note, image=image)

                return redirect('diaries:note_index')
    else:
        form = NoteForm()

    context = {
        'form': form,
        'diary': diary,
    }
    return render(request, 'diaries/createnote.html', context)



def comments_create(request, diary_pk, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.note = note
            comment.user = request.user
            comment.save()

        page = request.GET.get('page')
    return redirect(f'/diaries/?page={page}') 

def comments_delete(request, diary_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.delete()
    page = request.GET.get('page')
    return redirect(f'/diaries/?page={page}')  


def likes(request, diary_pk, note_pk):
    if request.method == "POST":
        note = Note.objects.get(pk=note_pk)
        if request.user in note.like_users.all():
            note.like_users.remove(request.user)
        else:
            note.like_users.add(request.user)

        page = request.GET.get('page')
        return redirect(f'/diaries/?page={page}')
    return redirect('diaries:note_index')
