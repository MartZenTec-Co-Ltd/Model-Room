"""Regression tests for settings geometry, switches and Apply/OK/Cancel semantics."""
import os, sys, tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK.parent))
from room_core import RoomStore
from room_preferences import save_preferences, load_preferences
from room_locale import LANGUAGES, tr
from room_controls import ToggleSwitch
from model_room import RoomWindow


def descendants(parent):
    for child in parent.winfo_children():
        yield child
        yield from descendants(child)


with TemporaryDirectory(dir=WORK) as directory:
    os.environ['MODELROOM_DATA_DIR'] = directory
    store = RoomStore(Path(directory))
    save_preferences(store, {'language':'zh-Hans','auto_detect_agents':False})
    root = tk.Tk(); root.attributes('-alpha',0)
    errors=[]
    root.report_callback_exception=lambda *args: errors.append(args)
    app=RoomWindow(root,store)
    app.suggest('unsent user draft')
    for code in LANGUAGES:
        for mode in ('light','dark'):
            app.apply_preferences({**app.preferences,'language':code,'mode':mode})
            app.open_settings()
            settings=app.settings_window
            assert not any(w.winfo_class()=='TCheckbutton' for w in descendants(settings.window))
            assert sum(isinstance(w,ToggleSwitch) for w in descendants(settings.window))==5
            for size in ('840x560','940x760'):
                settings.window.geometry(size)
                for page in settings.pages:
                    settings.select(page)
                    root.update()
                    window_top=settings.window.winfo_rooty()
                    footer_top=settings.footer.winfo_rooty()-window_top
                    assert footer_top+settings.footer.winfo_height()<=settings.window.winfo_height(), (code,mode,page,'footer clipped')
                    assert settings.pages[page].winfo_rooty()+settings.pages[page].winfo_height()<=settings.separator.winfo_rooty(), (code,mode,page,'page overlaps footer')
                    buttons=[settings.apply_button,settings.ok_button,settings.cancel_button]
                    assert all(b.winfo_ismapped() for b in buttons)
                    assert [b.winfo_rootx() for b in buttons]==sorted(b.winfo_rootx() for b in buttons)
                    assert buttons[-1].winfo_rootx()+buttons[-1].winfo_width()<=settings.window.winfo_rootx()+settings.window.winfo_width()-12
                    assert buttons[0].winfo_rootx()>settings.window.winfo_rootx()+settings.window.winfo_width()/2
                    if page=='connections':
                        viewport=settings.connection.canvas
                        right=viewport.winfo_rootx()+viewport.winfo_width()
                        clipped=[str(w.cget('text')) if 'text' in w.keys() else w.winfo_class()
                                 for w in descendants(viewport) if w.winfo_ismapped()
                                 and w.winfo_class() in ('TButton','TEntry','TCombobox','TLabel')
                                 and w.winfo_rootx()+w.winfo_width()>right+2]
                        assert not clipped, (code,mode,size,'clipped connection fields',clipped)
            settings.select('general'); root.update()
            switch=settings.auto_switch
            old=bool(settings.auto.get()); coordinates=switch.coords('thumb')
            switch.invoke(); root.update()
            assert bool(settings.auto.get()) is not old and coordinates!=switch.coords('thumb')
            assert str(settings.apply_button.cget('state'))=='normal'
            assert settings.cancel_button.cget('text')==tr('取消')
            switch.set_enabled(False); switch.invoke()
            assert bool(settings.auto.get()) is not old
            switch.set_enabled(True)
            switch.set_value(old)
            assert str(settings.apply_button.cget('state'))=='disabled'
            settings.dark_switch.invoke()
            expected='light' if mode=='dark' else 'dark'
            assert settings._values()['mode']==expected
            settings.dismiss()
            assert app.preferences['mode']==mode, 'Cancel must discard pending preferences'
            assert app.settings_window is None

    # Apply must keep the same dialog and preserve all unfinished fields, including keys.
    app.open_settings('connections'); root.update()
    s=app.settings_window; window_id=s.window.winfo_id()
    c=s.connection
    c.name.set('unsaved fixture connection')
    c.address.set('https://example.invalid/v1')
    c.model.set('fixture-model')
    c.key.insert(0,'fixture-not-a-real-key')
    c.search_key.insert(0,'fixture-search-key')
    c.tabs.select(1)
    s.accent.set('#a8347b')
    assert s.apply()
    root.update()
    assert s.window.winfo_exists() and s.window.winfo_id()==window_id
    assert app.settings_window is s and s.page=='connections'
    assert s.connection.tabs.index(s.connection.tabs.select())==1
    assert s.connection.name.get()=='unsaved fixture connection'
    assert s.connection.address.get()=='https://example.invalid/v1'
    assert s.connection.key.get()=='fixture-not-a-real-key'
    assert s.connection.search_key.get()=='fixture-search-key'
    assert load_preferences(store)['accent']=='#a8347b'
    assert app.composer.get('1.0','end-1c')=='unsent user draft'
    assert str(s.apply_button.cget('state'))=='disabled'
    # Invalid input and disk failures leave the dialog, drafts and saved prefs intact.
    before=dict(app.preferences)
    s.accent.set('invalid')
    with patch('room_settings_hub.messagebox.showerror') as showerror:
        assert not s.apply(); assert showerror.called
    assert app.preferences==before and s.window.winfo_exists()
    s.accent.set('#134678')
    with patch('model_room.save_preferences',side_effect=OSError('fixture disk failure')), patch('model_room.messagebox.showerror'):
        assert not s.apply()
    assert app.preferences==before and s.connection.key.get()=='fixture-not-a-real-key'
    # Language Apply rebuilds translated controls without dropping unfinished forms.
    s.language.set('English')
    assert s.apply(); root.update()
    assert s.apply_button.cget('text')=='Apply' and s.ok_button.cget('text')=='OK'
    assert s.connection.key.get()=='fixture-not-a-real-key'
    # OK saves and closes; subsequent Cancel keeps already applied values.
    s.accent.set('#23568a')
    assert s.accept(); root.update()
    assert app.settings_window is None and load_preferences(store)['accent']=='#23568a'
    app.open_settings(); root.update()
    app.settings_window.accent.set('#ffff00')
    app.settings_window.dismiss(); root.update()
    assert load_preferences(store)['accent']=='#23568a'
    assert not errors, errors
    app.close()
print('PASS: all 5 languages × 2 themes × 2 sizes × 7 settings pages; right-aligned fixed footer; Boolean switches; Apply retains dialog and connection drafts; OK/Cancel; invalid input and save failure; no stale callbacks.')
