from flask import (
    render_template, flash, url_for, redirect, request, abort, session
)
from flask_login import current_user, login_required
from . import main
from .forms import NoteForm, EditNoteForm
from ..auth.forms import LoginForm
from ..models import Note, User
from .. import db
from datetime import date, timedelta


@main.route('/', methods=['GET', 'POST'])
def index():
    note_form = NoteForm()
    login_form = LoginForm()
    if note_form.validate_on_submit():
        note = Note(
            note=note_form.note.data,
            author=current_user._get_current_object())
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('.index'))
    notes = []
    completion = 0
    if current_user.is_authenticated:
        notes = current_user.get_notes(date.today())
        completion = User.completion_rate(notes)
    return render_template('index.html', note_form=note_form,
        notes=notes, completion=completion)


@main.route('/complete-note/<int:id>')
@login_required
def complete_note(id):
    note = Note.query.get_or_404(id)
    if current_user != note.author:
        abort(403)
    note.status = True
    db.session.add(note)
    db.session.commit()
    flash('A task have been done!', category='success')
    return redirect(request.referrer)


@main.route('/edit-note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if current_user != note.author:
        abort(403)
    form = EditNoteForm()
    if form.validate_on_submit():
        note.note = form.note.data
        note.status = form.status.data
        db.session.add(note)
        db.session.commit()
        flash('The note has been updated.', category='info')
        return redirect(session.get('previous_url', url_for('main.index')))
    if request.method == 'GET':
        session['previous_url'] = request.referrer
    form.note.data = note.note
    form.status.data = note.status
    return render_template('edit_note.html', form=form, note=note)


@main.route('/delete-note/<int:id>')
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    if current_user != note.author:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted.', category='info')
    return redirect(session.get('previous_url', url_for('main.index')))


@main.route('/daily')
@login_required
def daily():
    group_notes = map(lambda x: (x[0], list(x[1])),
                      current_user.group_by_notes)
    return render_template('daily.html', group_notes=group_notes)


@main.route('/project')
def project():
    return render_template('project.html')


@main.route('/analysis')
def analysis():
    return render_template('analysis.html')


@main.route('/introduce')
def introduce():
    return render_template('introduce.html')