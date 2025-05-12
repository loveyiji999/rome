# map_editor_gui_v7.py - GUI 編輯器支援段落名稱 title 欄位

import tkinter as tk
from tkinter import messagebox
import yaml
import os
from core.custom_segment_manager import save_custom_segment, generate_new_custom_id

MAP_DIR = "data/maps"
SEGMENT_DEF_PATH = "data/track_config.yaml"
CUSTOM_SEG_PATH = "data/segments/custom_segments.yaml"

class MapEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("地圖編輯器 v7 - 支援段落名稱 title")

        self.map_listbox = tk.Listbox(master, width=30)
        self.map_listbox.grid(row=0, column=0, rowspan=12, sticky="ns")
        self.map_listbox.bind("<<ListboxSelect>>", self.load_selected_map)

        tk.Label(master, text="地圖名稱").grid(row=0, column=1, sticky="w")
        self.name_entry = tk.Entry(master, width=40)
        self.name_entry.grid(row=0, column=2)

        tk.Label(master, text="作者").grid(row=1, column=1, sticky="w")
        self.author_entry = tk.Entry(master, width=40)
        self.author_entry.grid(row=1, column=2)

        tk.Label(master, text="圈數").grid(row=2, column=1, sticky="w")
        self.laps_entry = tk.Entry(master, width=10)
        self.laps_entry.grid(row=2, column=2, sticky="w")

        tk.Label(master, text="段落順序").grid(row=3, column=1, columnspan=2, sticky="w")
        self.segment_listbox = tk.Listbox(master, height=10, width=40)
        self.segment_listbox.grid(row=4, column=1, columnspan=2)
        self.segment_listbox.bind("<<ListboxSelect>>", self.show_segment_attributes)

        tk.Button(master, text="↑ 上移", command=self.move_segment_up).grid(row=5, column=1, sticky="e")
        tk.Button(master, text="↓ 下移", command=self.move_segment_down).grid(row=5, column=2, sticky="w")
        tk.Button(master, text="刪除段落", command=self.delete_selected_segment).grid(row=6, column=1, sticky="w")
        tk.Button(master, text="儲存段落為自定義", command=self.save_segment_as_custom).grid(row=6, column=2, sticky="e")

        self.attr_box = tk.LabelFrame(master, text="段落屬性（可編輯）", padx=5, pady=5)
        self.attr_box.grid(row=7, column=1, columnspan=2, sticky="we")

        # 段落名稱欄位（title）
        tk.Label(self.attr_box, text="段落名稱 (title)").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.attr_box, width=30)
        self.title_entry.grid(row=0, column=1)

        self.attr_entries = {}

        self.save_btn = tk.Button(master, text="儲存地圖", command=self.save_map)
        self.save_btn.grid(row=8, column=1, sticky="e")

        self.delete_btn = tk.Button(master, text="刪除地圖", command=self.delete_map)
        self.delete_btn.grid(row=8, column=2, sticky="w")

        tk.Label(master, text="基礎段落清單").grid(row=0, column=3, sticky="w")
        self.base_segment_listbox = tk.Listbox(master, height=20, width=25)
        self.base_segment_listbox.grid(row=1, column=3, rowspan=8, sticky="n")
        self.base_segment_listbox.bind("<<ListboxSelect>>", self.append_segment_from_list)
        self.title_map = {}  # ID -> title
        self.segment_db = self.load_segment_defs()
        self.load_base_segment_list()
        self.load_map_list()

    def load_map_list(self):
        self.map_listbox.delete(0, tk.END)
        if not os.path.exists(MAP_DIR):
            os.makedirs(MAP_DIR)
        for fname in os.listdir(MAP_DIR):
            if fname.endswith(".yaml"):
                self.map_listbox.insert(tk.END, fname)

    def load_segment_defs(self):
        result = {}
        self.title_map.clear()
        for path in [SEGMENT_DEF_PATH, CUSTOM_SEG_PATH]:
            if not os.path.exists(path): continue
            with open(path, "r", encoding="utf-8") as f:
                segs = yaml.safe_load(f)
                for seg in segs:
                    result[seg["id"]] = seg["attributes"]
                    if "title" in seg:
                        self.title_map[seg["id"]] = seg["title"]
        return result
    
    def load_selected_map(self, event):
        if not self.map_listbox.curselection():
            return
        idx = self.map_listbox.curselection()[0]
        fname = self.map_listbox.get(idx)
        path = os.path.join(MAP_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.current_file = path
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))

        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, data.get("author", ""))

        self.laps_entry.delete(0, tk.END)
        self.laps_entry.insert(0, str(data.get("lap_count", 1)))

        self.segment_listbox.delete(0, tk.END)
        for seg in data.get("segments", []):
            self.segment_listbox.insert(tk.END, seg)
        self.show_segment_attributes()

    def load_base_segment_list(self):
        self.base_segment_listbox.delete(0, tk.END)
        for seg_id in sorted(self.segment_db.keys()):
            label = f"{seg_id}"
            if seg_id in self.title_map:
                label += f" - {self.title_map[seg_id]}"
            self.base_segment_listbox.insert(tk.END, label)

    def append_segment_from_list(self, event):
        idx = self.base_segment_listbox.curselection()
        if not idx: return
        label = self.base_segment_listbox.get(idx[0])
        seg_id = label.split(" - ")[0]
        self.segment_listbox.insert(tk.END, seg_id)

    def show_segment_attributes(self, event=None):
        for widget in self.attr_box.winfo_children():
            if isinstance(widget, tk.Entry) and widget != self.title_entry:
                widget.destroy()
        self.title_entry.delete(0, tk.END)

        idx = self.segment_listbox.curselection()
        if not idx:
            return
        seg_id = self.segment_listbox.get(idx[0])
        self.selected_segment_id = seg_id
        attr = self.segment_db.get(seg_id, {})
        if seg_id in self.title_map:
            self.title_entry.insert(0, self.title_map[seg_id])

        self.attr_entries.clear()
        row = 1
        for k, v in attr.items():
            tk.Label(self.attr_box, text=k).grid(row=row, column=0, sticky="w")
            e = tk.Entry(self.attr_box, width=20)
            e.insert(0, str(v))
            e.grid(row=row, column=1)
            self.attr_entries[k] = e
            row += 1

    def save_segment_as_custom(self):
        if not hasattr(self, "selected_segment_id"):
            messagebox.showwarning("未選取段落", "請先點選一個段落以編輯參數")
            return
        old_id = self.selected_segment_id
        new_attrs = {k: self.attr_entries[k].get() for k in self.attr_entries}
        for k in new_attrs:
            try:
                new_attrs[k] = float(new_attrs[k])
            except:
                pass
        new_id = generate_new_custom_id(old_id)
        new_data = {
            "id": new_id,
            "title": self.title_entry.get(),
            "track_type": old_id.split("_")[0] if "_" in old_id else old_id[:2],
            "attributes": new_attrs
        }
        save_custom_segment(new_data)
        self.segment_db[new_id] = new_attrs
        self.title_map[new_id] = new_data["title"]
        idx = self.segment_listbox.curselection()[0]
        self.segment_listbox.delete(idx)
        self.segment_listbox.insert(idx, new_id)
        self.segment_listbox.select_set(idx)
        self.load_base_segment_list()
        messagebox.showinfo("成功", f"段落已另存為 {new_id} 並套用至地圖")
        
    def move_segment_up(self):
        idx = self.segment_listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        item = self.segment_listbox.get(i)
        self.segment_listbox.delete(i)
        self.segment_listbox.insert(i - 1, item)
        self.segment_listbox.select_set(i - 1)

    def move_segment_down(self):
        idx = self.segment_listbox.curselection()
        if not idx or idx[0] >= self.segment_listbox.size() - 1:
            return
        i = idx[0]
        item = self.segment_listbox.get(i)
        self.segment_listbox.delete(i)
        self.segment_listbox.insert(i + 1, item)
        self.segment_listbox.select_set(i + 1)

    def delete_selected_segment(self):
        idx = self.segment_listbox.curselection()
        if not idx:
            return
        self.segment_listbox.delete(idx[0])
        self.title_entry.delete(0, tk.END)

    def save_map(self):
        if not hasattr(self, "current_file"):
            messagebox.showwarning("請選擇地圖", "請先從左側選取要儲存的地圖")
            return
        try:
            laps = int(self.laps_entry.get())
        except ValueError:
            messagebox.showerror("錯誤", "圈數必須是整數")
            return
        segments = [self.segment_listbox.get(i) for i in range(self.segment_listbox.size())]
        data = {
            "name": self.name_entry.get(),
            "author": self.author_entry.get(),
            "lap_count": laps,
            "segments": segments
        }
        with open(self.current_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        messagebox.showinfo("成功", "地圖已儲存！")

    def delete_map(self):
        if not hasattr(self, "current_file"):
            return
        if messagebox.askyesno("確認刪除", "確定要刪除此地圖？"):
            os.remove(self.current_file)
            self.load_map_list()
            self.name_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.laps_entry.delete(0, tk.END)
            self.segment_listbox.delete(0, tk.END)
            self.selected_segment_id = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MapEditorApp(root)
    root.mainloop()