"""Actual Settings integration: per-seat drafts, templates, import, save and cancel."""
import os
from pathlib import Path
import sys
import tempfile
import tkinter as tk
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from room_core import RoomStore
from room_group import Member,save_members,load_members
from room_preferences import save_preferences
from model_room import RoomWindow
from room_locale import LANGUAGES

with tempfile.TemporaryDirectory() as directory:
    os.environ['MODELROOM_DATA_DIR']=directory
    store=RoomStore(Path(directory))
    save_preferences(store,{'auto_detect_agents':False,'language':'en'})
    current=store.rooms()[0]
    members=[Member(str(i),f'AI-{i}','DeepSeek','fixture') for i in range(3)]
    save_members(store,current.id,members)
    root=tk.Tk()
    root.attributes('-alpha',0)
    errors=[]
    root.report_callback_exception=lambda *args: errors.append(args)
    app=RoomWindow(root,store)
    try:
        app.open_settings('personality')
        settings=app.settings_window
        editor=settings.personality
        root.update()
        editor.editor.insert('1.0','# First\nBe specific.\n')
        editor.choice.current(1); editor.select()
        editor.template.set('审阅伙伴'); editor.use_template()
        editor.choice.current(2); editor.select()
        imported=Path(directory)/'persona.md'
        imported.write_text('# Third\nUse examples.',encoding='utf-8')
        with patch('room_personality_ui.filedialog.askopenfilename',return_value=str(imported)):
            editor.import_markdown()
        imported.unlink()
        root.update()
        assert editor.dirty
        assert settings.apply()
        loaded=load_members(store,current.id,app.active_profile())
        assert loaded[0].personality=='# First\nBe specific.'
        assert 'Constructive reviewer' in loaded[1].personality
        assert loaded[2].personality=='# Third\nUse examples.'
        assert not editor.dirty
        editor.editor.insert('end','UNSAVED')
        root.update()
        settings.dismiss()
        assert all('UNSAVED' not in member.personality for member in load_members(store,current.id,app.active_profile()))
        for code in LANGUAGES:
            app.apply_preferences({**app.preferences,'language':code})
            app.open_settings('personality')
            settings=app.settings_window
            settings.window.geometry('840x560')
            root.update()
            editor=settings.personality
            assert editor.editor.winfo_ismapped()
            assert settings.footer.winfo_rooty()+settings.footer.winfo_height()<=settings.window.winfo_rooty()+settings.window.winfo_height()
            settings.dismiss()
        assert not errors,errors
    finally:
        app.close()
print('PASS: three independent personalities, packaged template, Markdown import, Apply/Cancel, and five-language settings geometry.')
