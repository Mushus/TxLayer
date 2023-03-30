import bpy
import os, csv, codecs #辞書
import sys

def preference():
	preference = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences

	return preference


# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")

	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			for context in bpy.app.translations.contexts:
				dict['ja_JP'][(context, row[1].replace('\\n', '\n'))] = row[0].replace('\\n', '\n')

	return dict

# アドオン内のmoduleフォルダーを、import時に検索されるパスリストに追加する
def set_module_path_to_sys():
	tgt_dir = os.path.dirname(os.path.abspath(__file__))
	if os.path.join(tgt_dir,"module") in sys.path:
		return

	basename = tgt_dir.replace(" ","$SPACE_DUMMY_CTPLayers")
	path_l = [os.path.join(basename,"module")]
	for pt in path_l:
		sys.path.append(pt)
	for i,pt in enumerate(sys.path):
		if pt == path_l[0]:
			sys.path[i] = sys.path[i].replace("$SPACE_DUMMY_CTPLayers"," ")
