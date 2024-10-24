from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Note, NoteImage, Comment
from .forms import NoteForm, NoteImageForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
@login_required
def index(request):
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
    }
    return render(request, 'notes/index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        # form = NoteForm(request.POST, request.FILES)
        form = NoteForm(request.POST)
        images = request.FILES.getlist('image') 

        if form.is_valid():
            note = form.save(commit=False)
            note.diary_id = form.cleaned_data['diary_id']
            note.note_writer = request.user
            note.save()

            # 이미지 개수 제한
            # for image in images:
            #     NoteImage.objects.create(note=note, image=image)

            if len(images) > 3:
                form.add_error(None, "이미지는 최대 3개까지만 업로드할 수 있습니다.")
            else:
                for image in images:
                    NoteImage.objects.create(note=note, image=image)

                return redirect('notes:index')
    else:
        form = NoteForm()

    context = {
        'form': form,
    }
    return render(request, 'notes/create.html', context)




def comments_create(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.note = note
            comment.user = request.user
            comment.save()

        page = request.GET.get('page')
    return redirect(f'/notes/?page={page}') 

def comments_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.delete()
    page = request.GET.get('page')
    return redirect(f'/notes/?page={page}')  


def likes(request, note_pk):
    if request.method == "POST":
        note = Note.objects.get(pk=note_pk)
        if request.user in note.like_users.all():
            note.like_users.remove(request.user)
        else:
            note.like_users.add(request.user)

        page = request.GET.get('page')
        return redirect(f'/notes/?page={page}')
    return redirect('notes:index')
