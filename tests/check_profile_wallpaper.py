"""Full viewport wallpaper, identities, input preferences and expanded settings regression."""
import json, os, sys, time, tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(WORK.parent))
from PIL import Image
from model_room import RoomWindow, Timeline
from room_core import RoomStore, context_for, DEEPSEEK
from room_identity import import_avatar, avatar_path, avatar_data_url, room_nickname
from room_preferences import save_preferences, load_preferences, import_wallpaper, wallpaper_image
from room_locale import LANGUAGES, tr
from room_wallpaper import WallpaperTimeline
from room_export import export_chat

def settle(root, seconds=.2):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        root.update(); time.sleep(.015)

with TemporaryDirectory(dir=WORK) as directory:
    directory=Path(directory); os.environ['MODELROOM_DATA_DIR']=str(directory)
    store=RoomStore(directory)
    save_preferences(store,{'language':'zh-Hans','auto_detect_agents':False})
    root=tk.Tk(); root.attributes('-alpha',0)
    errors=[]; root.report_callback_exception=lambda *args:errors.append(args)
    app=RoomWindow(root,store)
    first=app.current_room
    other=store.add_room('Other room')
    source=directory/'source.jpg'
    exif=Image.Exif(); exif[315]='Private metadata fixture'
    Image.new('RGB',(1000,500),'#a62460').save(source,exif=exif)
    wall=import_wallpaper(source,directory)
    profile=import_avatar(source,directory)
    source.unlink()
    with Image.open(profile) as photo:
        assert photo.size==(256,256) and photo.mode=='RGBA' and photo.getpixel((0,0))[3]==0
        assert not photo.getexif() and 'exif' not in photo.info
    with Image.open(wall) as photo:
        assert not photo.getexif() and 'exif' not in photo.info
    assert avatar_path(directory,'../source.jpg') is None
    assert avatar_path(directory,'avatar-aaaaaaaaaaaaaaaaaaaa.png').parent==directory/'avatars'
    assert avatar_data_url(directory,Path(profile).name).startswith('data:image/png;base64,')
    for fit in ('cover','contain','tile'):
        image=wallpaper_image({'wallpaper':wall,'wallpaper_opacity':100,'wallpaper_fit':fit},700,320,'#ffffff')
        assert image.size==(700,320)
        assert image.getpixel((350,160))!=(255,255,255)

    app.open_settings(); settings=app.settings_window
    assert list(settings.pages)==['general','connections','appearance','chat','storage','about']
    settings.nickname.set('Alice')
    settings.room_nickname.set('本群 Alice')
    settings.options['avatar']=profile
    settings.options['wallpaper']=wall
    settings.opacity.set(100)
    settings.send_enter.set(False)
    settings.auto_scroll.set(False)
    settings.default_rounds.set('9')
    assert settings.apply(); settle(root)
    assert app.settings_window is settings and settings.window.winfo_exists()
    assert app.local_name()=='本群 Alice' and room_nickname(store,first.id)=='本群 Alice'
    assert app.rounds.get()=='9' and not app.preferences['send_with_enter']
    assert isinstance(app.timeline,WallpaperTimeline)
    assert app.wallpaper_image.width()==app.timeline.view.winfo_width()
    assert app.wallpaper_image.height()==app.timeline.view.winfo_height()
    assert app.wallpaper_image.height()>84,'Wallpaper must cover the complete viewport, not a banner'
    own=app.append_message(first.id,'你','first signed message',(DEEPSEEK,))
    assert own.author=='你' and own.details['display_name']=='本群 Alice'
    assert Path(own.details['avatar_asset']).name==Path(profile).name
    assert '本群 Alice' in context_for([own],DEEPSEEK)
    for index in range(25):
        app.append_message(first.id,'Fixture AI','Long response 中文日本語한국어 '+str(index)+'\n'+('Line of text. '*20))
    settle(root)
    for size in ('970x640','1230x760'):
        root.geometry(size); settle(root)
        canvas=app.timeline.view
        assert (app.wallpaper_image.width(),app.wallpaper_image.height())==(canvas.winfo_width(),canvas.winfo_height())
        assert len(canvas.find_withtag('wallpaper'))==1
        for position in (0,.4,1):
            canvas.yview_moveto(position); settle(root,.04)
            assert abs(canvas.coords(app.timeline.background_item)[1]-canvas.canvasy(0))<2
    assert any('first signed message' in str(app.timeline.view.itemcget(item,'text'))
               for item in app.timeline.view.find_all() if app.timeline.view.type(item)=='text'), 'Wallpaper must not hide messages'
    app.timeline.view.yview_moveto(.4); settle(root,.04)
    reading_y=app.timeline.view.canvasy(0)
    app.append_message(first.id,'Fixture AI','A new reply must not move the reading position.\n'+('Reply '*100))
    settle(root)
    assert abs(app.timeline.view.canvasy(0)-reading_y)<25

    settings.nickname.set('Alice changed')
    settings.room_nickname.set('Room changed')
    settings.options['avatar']=''
    assert settings.apply(); settle(root)
    later=app.append_message(first.id,'你','later signed message',(DEEPSEEK,))
    assert later.details['display_name']=='Room changed'
    original=next(m for m in store.recent(first.id) if m.body=='first signed message')
    assert original.details['display_name']=='本群 Alice' and original.details['avatar_asset']==Path(profile).name
    for suffix in ('md','txt','json'):
        target=directory/('history.'+suffix); export_chat(store,first,target)
        body=target.read_text(encoding='utf-8')
        assert '本群 Alice' in body and 'Room changed' in body
        assert 'avatar-' not in body and str(directory) not in body
    with patch.object(app.lan,'share_cutoff',return_value=0),patch.object(app.lan,'publish') as publish:
        app.publish_room(first.id)
        payload=publish.call_args.args[1]
        assert payload['host_name']=='Room changed'
        first_payload=next(m for m in payload['messages'] if m['body']=='first signed message')
        assert first_payload['author']=='本群 Alice' and first_payload['avatar'].startswith('data:image/png;base64,')
        assert str(directory) not in json.dumps(payload)
    settings.dismiss(); app.activate_room(other); settle(root)
    assert app.local_name()=='Alice changed' and room_nickname(store,other.id)==''
    assert app.rounds.get()=='9'
    with patch.object(app,'send') as send:
        assert app.send_on_enter(SimpleNamespace(state=0)) is None
        assert app.send_on_enter(SimpleNamespace(state=4))=='break' and send.call_count==1
        assert app.send_on_enter(SimpleNamespace(state=1)) is None

    for code in LANGUAGES:
        app.apply_preferences({**app.preferences,'language':code})
        app.open_settings(); s=app.settings_window
        s.window.geometry('840x560')
        for page in s.pages:
            s.select(page); settle(root,.025)
            assert s.cancel_button.winfo_ismapped()
            assert s.footer.winfo_rooty()+s.footer.winfo_height()<=s.window.winfo_rooty()+s.window.winfo_height()
            assert s.apply_button.winfo_rootx()>s.window.winfo_rootx()+s.window.winfo_width()/2
        s.nickname.set('pending')
        s.room_nickname.set('pending room')
        s.dismiss()
        assert app.preferences['nickname']=='Alice changed' and room_nickname(store,other.id)==''
    app.apply_preferences({**app.preferences,'wallpaper':'','message_font_size':16,'show_timestamps':False})
    settle(root)
    assert isinstance(app.timeline,Timeline)
    assert int(root.tk.call('font','actual',app.composer.cget('font'),'-size'))==16
    hidden_time=app.append_message(other.id,'你','Timestamp visibility fixture')
    settle(root,.05)
    assert hidden_time.time[11:16] not in app.timeline.rows[-1][0].meta.cget('text')
    literal=store.add(other.id,'你','Literal nickname',details={'display_name':'设置'})
    app.timeline.add(literal)
    assert app.timeline.rows[-1][0].meta.cget('text')=='设置','Never translate a custom nickname even when times are hidden'
    assert not errors,errors
    app.close()
    reopened=RoomStore(directory)
    assert load_preferences(reopened)['nickname']=='Alice changed'
    assert room_nickname(reopened,first.id)=='Room changed'
    assert room_nickname(reopened,other.id)==''
    reopened.close()
print('PASS: full wallpaper viewport with visible messages and scroll/resize; 3 fit modes; safe avatars; global and per-room nickname snapshots; context/export/LAN names; input settings; six pages × five languages; cancellation and restart persistence; no callback errors.')
