""""
"""
import json
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox, scrolledtext
import keys
# Trying to import modules that needs installation
try:
    from ibm_watson import LanguageTranslatorV3
    from ibm_watson import ApiException
    from PIL import Image, ImageTk
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
except ImportError as e:
    from pip._internal import  main as install
    install(["install", "pillow"])
    install(["install", "ibm-watson>=4.7.1"])
finally:
    pass

# Creating custom Exceptions
class SameLanguageException(Exception):
    pass
class NoTextException(Exception):
    pass
# creating a tkinter window
root = Tk()
root.title("Language Translator")
root.iconbitmap("main.ico")
window_width, window_height = 1000,450
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
position_top,position_right = int(screen_height/2 - window_height/2), int(screen_width/2 - window_width/2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
root.resizable(False, False)

# Translator and API consumption
authenticator = IAMAuthenticator(f'{keys.apikey}')
language_translator = LanguageTranslatorV3(
    version=f'{keys.version}',
    authenticator=authenticator
)
language_translator.set_service_url(f'{keys.url}')
# Functions
def close():
    val = messagebox.askyesnocancel("Language Translator", "Are you sure you want to close the Language Translator "
                                                           "App?")
    return root.quit() or root.destroy() if val else root.focus()
def clear(yes):
    if yes:
        val = messagebox.askokcancel("Language Translator",
                                 "By clearing, you will "
                                 "loose all the infomation you have typed")
        if val:
            text_before.delete('0.0', END)
            text_after.delete('0.0', END)
        else:
            root.focus()
    else:
        text_after.delete('0.0', END)
        return
    return
def translate():
    clear(False)
    first_langauge = lang1.get() # the language that is being translated
    second_language = lang2.get() # the languge that will be translated
    raw_text = text_before.get('0.0', END)
    if first_langauge == second_language:
        # raise an exeptions langages must be diffrent
        raise SameLanguageException("The Two Languages Must Be Diffrent Indorder For The Translation To Take Effect.")
    if len(raw_text) == 0:
        # raise an exception text is required
        raise NoTextException("The Text Being Translated Can Not Be Empty.")
    # try to translate
    try:
        try:
            # en-es => english to espa...
            model_id = '{0}-{1}'.format(first_langauge, second_language)
            translation = language_translator.translate(raw_text, model_id=model_id).result
            # get word count
            word_count = f'Words In The Translation:\t{translation["word_count"]}\n'
            # get translation
            translation_text = f'Translation Text: \t{translation["translations"][0]["translation"]}\n'
            # get character count for translation
            character_count = f'Characters in the translati' \
                              f'on:\t {translation["character_count"]}\n'
            text_after.insert(END, translation_text)
            text_after.insert(END, word_count)
            text_after.insert(END, character_count)
            # print(translation)
        except Exception as e:
            messagebox.showerror("Language Translator", e)
        finally:
            pass
    except ApiException as e:
        messagebox.showerror("Language Translator", "Make sure you are connected to internet and your API credentials are working.")
    finally:
        pass

    return
# Global variables
lang1 = StringVar()
lang2 = StringVar()
langages =[]
try:
    language_result= language_translator.list_languages().get_result()
    # print(json.dumps(language_result, indent=2))
    for i in language_result["languages"]:
        langages.append(i["language"])
except ApiException as e:
    print(e)
lang1.set(langages[16]) # From English as default
lang2.set(langages[23]) # to French as defalt


#  Pushing The langages and their Id's in the language helper
def pushIds():
    langages_and_ids["state"] = NORMAL
    language_result = language_translator.list_languages().get_result()
    for language in language_result["languages"]:
        # print(language)
        row = f'{language["language_name"]} ({language["language"]})\n'
        langages_and_ids.insert(END, row)
    langages_and_ids["state"] = DISABLED
    return
# UI
label_image = ImageTk.PhotoImage(Image.open("main.ico"))
label1 = Label(root, text="", font=("arial", 15, "bold"), fg="lightseagreen", image=label_image,
       compound=RIGHT)
label1.grid(row=0, column=0, columnspan=6)
label1 = Label(root, text="Text Before Translated", font=("arial", 12, "bold"), fg="lightseagreen")
label1.grid(row=2, column=0, columnspan=3)
label1 = Label(root, text="Language Id Helper", font=("arial", 12, "bold"), fg="lightseagreen")
label1.grid(row=2, column=5, columnspan=3)

langages_and_ids = scrolledtext.ScrolledText(root, width=30, height=15, font=("arial", 10), state=DISABLED)
langages_and_ids.grid(row=3, column=5, rowspan=8, padx=10, pady=10)
text_before = scrolledtext.ScrolledText(root, width=48, height=5, font=("arial", 12))
text_before.grid(row=3, column=0, columnspan=3, rowspan=3, padx=10, pady=10)
label1 = Label(root, text="Select Langage", font=("arial", 10))
label1.grid(row=3, column=3)
language_options_before = OptionMenu(root,lang1,*langages)
language_options_before.grid(row=3, column=4, ipadx=50, padx=5)
Button(root, bg="green", relief="solid", activebackground="blue",
       text="translate" ,fg="white", width=15, bd=1, command=translate).grid(
    row=4, column=3)
Button(root, bg="orange", relief="solid", activebackground="red",
       text="clear" ,fg="white", width=15, bd=1, command=lambda : clear(True)).grid(
    row=5, column=3)
label1 = Label(root, text="Text After Translated", font=("arial", 12, "bold"), fg="lightseagreen")
label1.grid(row=6, column=0, columnspan=3)
text_after = scrolledtext.ScrolledText(root, width=48, height=5, font=("arial", 12))
text_after.grid(row=7, column=0, columnspan=3, rowspan=3, padx=10, pady=10)
label1 = Label(root, text="Select Langage", font=("arial", 10))
label1.grid(row=7, column=3)
language_options_before = OptionMenu(root,lang2,*langages)
language_options_before.grid(row=7, column=4, ipadx=50, padx=5)
Button(root, bg="orange", relief="solid", activebackground="red",
       text="close",fg="white", width=15, bd=1, command =close).grid(
    row=10, column=0, sticky=W, padx=5, pady=5)
# call the push Id's after everything is loaded
pushIds()
root.mainloop(0)