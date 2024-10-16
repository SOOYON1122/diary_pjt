from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DiaryForm, NoteForm, NoteImageForm


# Create your views here.
def index(request):
  return render(request, 'diaries/index.html')


def creatediary(request):
  if request.method == 'POST':
    form = DiaryForm(request.POST, request.FILES)
    if form.is_valid():
      diary = form.save(commit=False)
      diary.user = request.user
      diary.save()
      return redirect('diaries:diary_detail', diary.id)
  else:
    form = DiaryForm(user=request.user)

  context = {
    'form': form,
  }
  return render(request, 'diaries/creatediary.html', context)


def mydiary(request):
  pass