"""Cross-platform regressions: 3 real adapter calls per round against offline fixtures."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from room_core import RoomStore
from room_group import Member, Target, DiscussionControl, load_members, save_members, run_rounds
from room_personality import clean_personality, read_personality
from room_providers import Profile, ask_profile
from room_platform import child_environment


class DiscussionTests(unittest.TestCase):
    def test_three_members_share_peer_replies_and_human_note(self):
        targets = tuple(Target(Member(str(i),f'AI-{i}',str(i),'fixture',f'PERSONA-{i}'),
                        Profile(str(i),f'AI-{i}','https://fixture.invalid','fixture'), '') for i in range(3))
        control = DiscussionControl(3)
        requests, events = [], []
        lock = threading.Lock()

        def http(_url,_headers,payload=None,**_kwargs):
            with lock:
                requests.append(payload)
            # Synthetic API response: the test verifies real adapter payloads, not AI quality.
            name = next(target.member.name for target in targets if target.member.name in payload['messages'][0]['content'])
            return {'model':'fixture','choices':[{'message':{'content':f'REPLY-{name}'}}]},200,None,0

        def call(target,text,context):
            result = ask_profile(target.profile,text,context,'',personality=target.member.personality)
            return result.body,result.details

        def emit(event,author,body,details):
            events.append((event,author,body))
            if event=='phase' and '1/3' in body:
                control.request_pause()
            if event=='phase' and body=='已暂停，等你发言':
                control.add_human('Human','NEW-REQUIREMENT',resume=True)

        with patch('room_core.http_json',side_effect=http):
            result = run_rounds('TOPIC',targets,[],False,'',True,control,call,emit)
        self.assertEqual(result,'讨论完成')
        self.assertEqual(len(requests),9)
        self.assertTrue(any('已暂停' in body for _,_,body in events))
        for payload in requests:
            system,user = (message['content'] for message in payload['messages'])
            own = next(i for i in range(3) if f'PERSONA-{i}' in system)
            self.assertFalse(any(f'PERSONA-{other}' in system for other in range(3) if other!=own))
            if '自由讨论第 1 轮' not in user:
                for other in range(3):
                    self.assertIn(f'REPLY-AI-{other}',user)
                self.assertIn('NEW-REQUIREMENT',user)

    def test_failed_member_does_not_stop_other_two(self):
        targets = tuple(Target(Member(str(i),f'AI-{i}')) for i in range(3))
        calls=[]
        def call(target,text,context):
            calls.append(target.member.id)
            if target.member.id=='0':
                raise RuntimeError('fixture failure')
            return 'fixture reply',{}
        self.assertEqual(run_rounds('topic',targets,[],False,'',True,DiscussionControl(3),call,
                                    lambda *args:None),'讨论完成')
        self.assertEqual(calls.count('0'),1)
        self.assertEqual(calls.count('1'),3)
        self.assertEqual(calls.count('2'),3)

    def test_empty_roster_is_safe(self):
        # Public caller prevents empty runs; direct invocation must also handle it.
        self.assertEqual(run_rounds('topic',(),[],False,'',True,DiscussionControl(2),
                                   lambda *args:None,lambda *args:None),'讨论提前结束')


class PersonalityTests(unittest.TestCase):
    def test_legacy_and_per_room_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            store = RoomStore(Path(directory))
            try:
                store.set_group('legacy',[{'id':'a','name':'A','provider_id':'p','model':'m'}])
                profile=Profile('p','P','https://fixture.invalid','m')
                self.assertEqual(load_members(store,'legacy',profile)[0].personality,'')
                save_members(store,'a',[Member('a','A','p','m','# Reviewer\nBe specific.')])
                save_members(store,'b',[Member('a','A','p','m','# Builder\nOffer alternatives.')])
                self.assertIn('Reviewer',load_members(store,'a',profile)[0].personality)
                self.assertIn('Builder',load_members(store,'b',profile)[0].personality)
            finally:
                store.close()

    def test_markdown_is_text_with_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'personality.md'
            path.write_text('\ufeff# Reviewer\nUse evidence.',encoding='utf-8')
            self.assertEqual(read_personality(path),'# Reviewer\nUse evidence.')
            path.write_bytes(b'x'*65537)
            with self.assertRaises(ValueError): read_personality(path)
            path.write_bytes(b'\xff\xfe')
            with self.assertRaises(ValueError): read_personality(path)
        with self.assertRaises(ValueError): clean_personality('x'*12001)
        with self.assertRaises(ValueError): clean_personality('a\0b')

    def test_anthropic_system_receives_personality(self):
        with patch('room_providers.http_json',return_value=({'content':[{'type':'text','text':'fixture'}]},200,None,0)) as http:
            ask_profile(Profile('p','P','https://fixture.invalid','fixture',transport='anthropic'),
                        'topic','[]','',personality='# Reviewer')
            self.assertIn('# Reviewer',http.call_args.args[2]['system'])

    @unittest.skipIf(os.name=='nt','Unix file permissions')
    def test_unix_secret_roundtrip_tamper_and_permissions(self):
        from win_secrets import read_secret,write_secret
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'keys/provider.key'
            write_secret(path,'synthetic-credential')
            self.assertEqual(read_secret(path),'synthetic-credential')
            self.assertNotIn(b'synthetic-credential',path.read_bytes())
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            self.assertEqual((path.parent/'.modelroom-vault-key').stat().st_mode & 0o777,0o600)
            path.write_bytes(path.read_bytes()[:-1]+b'!')
            self.assertEqual(read_secret(path),'')
            path.chmod(0o644)
            self.assertEqual(read_secret(path),'')

    def test_frozen_environment_does_not_leak_bundled_libraries(self):
        with patch.object(sys,'frozen',True,create=True),patch.dict(os.environ,{'LD_LIBRARY_PATH':'/bundle',
                 'LD_LIBRARY_PATH_ORIG':'/system','PYTHONHOME':'/bundle','TK_LIBRARY':'/bundle'}):
            env=child_environment()
            self.assertEqual(env['LD_LIBRARY_PATH'],'/system')
            self.assertNotIn('PYTHONHOME',env)
            self.assertNotIn('TK_LIBRARY',env)


if __name__=='__main__':
    unittest.main()
