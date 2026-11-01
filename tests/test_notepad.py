"""Exercise generated URLs, version selection, draft omission and validation."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]

class NotepadTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'scripts').mkdir()
        shutil.copy2(SOURCE/'scripts/build_notepad.py', self.root/'scripts/build_notepad.py')
        spec=importlib.util.spec_from_file_location('notepad', self.root/'scripts/build_notepad.py')
        self.module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        (self.root/'notepad/media').mkdir(parents=True)
        for name in ('one.mp3','two.mp3','image.png'):
            (self.root/'notepad/media'/name).write_bytes(b'fixture')
        self.entry={'slug':'test-entry','title':'A < B','draft':False,'published':'2026-10-01','updated':'2026-11-01','notes':['<script>alert(1)</script>'], 'featuredVersion':'v1','versions':[
            {'id':'v1','label':'Earlier recording','date':'2026-10-01','audio':'notepad/media/one.mp3'},
            {'id':'v2','label':'Newer recording','date':'2026-11-01','audio':'notepad/media/two.mp3'}],
            'images':[{'src':'notepad/media/image.png','alt':'Test image'}], 'feedImage':0}
        self.data={'schemaVersion':1,'entries':[self.entry]}

    def tearDown(self): self.temp.cleanup()

    def test_featured_is_independent_of_latest(self):
        self.module.validate(self.data)
        pages=dict(self.module.render(self.data))
        feed=pages[Path('notepad/index.html')]
        detail=pages[Path('notepad/test-entry/index.html')]
        self.assertIn('../notepad/media/one.mp3',feed)
        self.assertNotIn('two.mp3',feed)
        self.assertIn('../../notepad/media/two.mp3',detail)
        self.assertIn('../../notepad/media/one.mp3',detail)
        self.assertLess(detail.index('id="v2"'),detail.index('id="v1"'))
        self.assertIn('controlslist="nodownload"', detail)
        self.assertNotIn('<script>alert',detail)
        self.assertIn('&lt;script&gt;',detail)
        self.assertIn('A &lt; B',feed)
        self.assertIn('src="../notepad/media/image.png"',feed)
        self.assertNotIn(' download>',detail)

    def test_drafts_and_empty_feed(self):
        self.entry['draft']=True
        pages=dict(self.module.render(self.data))
        self.assertEqual(len(pages),1)
        self.assertNotIn('test-entry',pages[Path('notepad/index.html')])

    def test_invalid_assets_and_selection_fail(self):
        self.entry['featuredVersion']='missing'
        with self.assertRaises(ValueError): self.module.validate(self.data)
        self.entry['featuredVersion']='v1'
        self.entry['versions'][0]['audio']='../../secret.mp3'
        with self.assertRaises(ValueError): self.module.validate(self.data)

    def test_select_feature_and_remove_stale_draft_page(self):
        catalog=self.root/'notepad/entries.json'
        catalog.write_text(json.dumps(self.data))
        run=lambda *args: subprocess.run([sys.executable,str(self.root/'scripts/build_notepad.py'),*args],check=True,capture_output=True)
        run('--feature','test-entry','v2')
        saved=json.loads(catalog.read_text())
        self.assertEqual(saved['entries'][0]['featuredVersion'],'v2')
        self.assertEqual(saved['entries'][0]['published'],'2026-10-01')
        self.assertEqual(len(saved['entries'][0]['versions']),2)
        self.assertIn('two.mp3',(self.root/'notepad/index.html').read_text())
        saved['entries'][0]['draft']=True
        catalog.write_text(json.dumps(saved))
        run()
        self.assertFalse((self.root/'notepad/test-entry/index.html').exists())

if __name__=='__main__': unittest.main()
