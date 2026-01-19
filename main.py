from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import os

# ملفات قاعدة البيانات المحلية
USERS_DB = "users_list.txt" 
SALES_DB = "sales_history.txt"

class BiometricSystem(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        
        self.add_widget(Label(text="نظام الهوية الوطنية وصرف الحصص", font_size='22sp', color=(1, 1, 0, 1)))
        
        # مدخلات البيانات
        self.nin_in = TextInput(hint_text="رقم التعريف الوطني (NIN)", multiline=False, size_hint_y=None, height=50)
        self.name_in = TextInput(hint_text="الاسم الكامل للمواطن", multiline=False, size_hint_y=None, height=50)
        self.fam_in = TextInput(hint_text="رقم بطاقة العائلة", multiline=False, size_hint_y=None, height=50)
        
        self.add_widget(self.nin_in)
        self.add_widget(self.name_in)
        self.add_widget(self.fam_in)
        
        # أزرار العمليات
        self.reg_btn = Button(text="تسجيل مواطن جديد", background_color=(0, 0.7, 0, 1), height=60, size_hint_y=None)
        self.reg_btn.bind(on_press=self.register_citizen)
        self.add_widget(self.reg_btn)
        
        self.check_btn = Button(text="تحقق وبصمة وصرف الحصة", background_color=(0.2, 0.6, 1, 1), height=60, size_hint_y=None)
        self.check_btn.bind(on_press=self.verify_identity)
        self.add_widget(self.check_btn)
        
        self.status = Label(text="في انتظار المسح البيومتري...", font_size='16sp')
        self.add_widget(self.status)

    def register_citizen(self, instance):
        nin, name, fam = self.nin_in.text.strip(), self.name_in.text.strip(), self.fam_in.text.strip()
        if nin and name and fam:
            with open(USERS_DB, "a", encoding='utf-8') as f:
                f.write(f"{nin}:{name}:{fam}\n")
            self.status.text = f"✅ تم تسجيل المواطن: {name}"
            self.clear_fields()
        else:
            self.status.text = "⚠️ يرجى ملء كافة الخانات!"

    def verify_identity(self, instance):
        nin = self.nin_in.text.strip()
        citizen_data = self.get_citizen_info(nin)
        
        if citizen_data:
            nin_val, name_val, fam_id = citizen_data
            
            # حساب عدد أفراد العائلة المسجلين بنفس الرقم العائلي
            members_count = self.count_family_members(fam_id)
            
            if self.is_already_served(fam_id):
                self.status.text = f"❌ رفض! عائلة {name_val} استلمت مسبقاً.\n(إجمالي أفراد العائلة: {members_count})"
                self.status.color = (1, 0, 0, 1)
            else:
                self.record_serving(fam_id)
                self.status.text = f"✅ تم التحقق: {name_val}\nعائلة: {fam_id} | الأفراد: {members_count}\nتم تسجيل عملية الصرف."
                self.status.color = (0, 1, 0, 1)
        else:
            self.status.text = "❌ الرقم الوطني غير موجود في السجل!"

    def count_family_members(self, fam_id):
        count = 0
        if os.path.exists(USERS_DB):
            with open(USERS_DB, "r", encoding='utf-8') as f:
                for line in f:
                    if f":{fam_id}" in line.strip():
                        count += 1
        return count

    def get_citizen_info(self, nin):
        if os.path.exists(USERS_DB):
            with open(USERS_DB, "r", encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(":")
                    if parts[0] == nin: return parts
        return None

    def is_already_served(self, fam_id):
        if os.path.exists(SALES_DB):
            with open(SALES_DB, "r") as f:
                return fam_id in f.read()
        return False

    def record_serving(self, fam_id):
        with open(SALES_DB, "a") as f:
            f.write(f"{fam_id}\n")

    def clear_fields(self):
        self.nin_in.text = ""; self.name_in.text = ""; self.fam_in.text = ""

class BiometricApp(App):
    def build(self): return BiometricSystem()

if __name__ == '__main__':
    BiometricApp().run()

