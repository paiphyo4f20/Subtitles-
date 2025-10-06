#!/usr/bin/env python3
"""
Myanmar Subtitle Translator
A simple script to translate SRT files from English to Myanmar
"""

import os
import re
import json
import time
from pathlib import Path
from googletrans import Translator

class SubtitleTranslator:
    def __init__(self):
        self.translator = Translator()
        self.translation_memory = self.load_memory()
        
    def load_memory(self):
        """Load translation memory from file"""
        try:
            with open('translation_memory.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_memory(self):
        """Save translation memory to file"""
        with open('translation_memory.json', 'w', encoding='utf-8') as f:
            json.dump(self.translation_memory, f, ensure_ascii=False, indent=2)
    
    def parse_srt(self, file_path):
        """Parse SRT file and extract subtitles"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subtitles = []
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                subtitle = {
                    'id': int(lines[0]),
                    'timing': lines[1],
                    'original_text': '\n'.join(lines[2:]),
                    'translated_text': '',
                    'needs_review': False
                }
                subtitles.append(subtitle)
        
        return subtitles
    
    def translate_text(self, text):
        """Translate English text to Myanmar using Google Translate"""
        if not text.strip():
            return text
        
        # Check memory first
        if text in self.translation_memory:
            return self.translation_memory[text]
        
        try:
            # Translate using Google Translate
            translated = self.translator.translate(text, src='en', dest='my')
            result = translated.text
            
            # Save to memory
            self.translation_memory[text] = result
            return result
            
        except Exception as e:
            print(f"Translation error for '{text}': {e}")
            return f"[Translation Error: {text}]"
    
    def auto_translate_all(self, subtitles):
        """Auto-translate all subtitles"""
        print("🔄 Auto-translating all subtitles...")
        
        for i, subtitle in enumerate(subtitles):
            # Skip if it's a timing line or number
            if re.match(r'^\d+$', subtitle['original_text'].strip()):
                continue
            if '-->' in subtitle['original_text']:
                continue
            
            print(f"Translating line {i+1}/{len(subtitles)}: {subtitle['original_text'][:50]}...")
            subtitle['translated_text'] = self.translate_text(subtitle['original_text'])
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        print("✅ Auto-translation complete!")
        return subtitles
    
    def export_srt(self, subtitles, output_path):
        """Export translated subtitles to SRT file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for subtitle in subtitles:
                f.write(f"{subtitle['id']}\n")
                f.write(f"{subtitle['timing']}\n")
                f.write(f"{subtitle['translated_text']}\n\n")
    
    def interactive_review(self, subtitles):
        """Interactive review and editing interface"""
        print("\n" + "="*50)
        print("🎌 INTERACTIVE REVIEW MODE")
        print("="*50)
        
        i = 0
        while i < len(subtitles):
            sub = subtitles[i]
            
            # Skip timing/number lines
            if re.match(r'^\d+$', sub['original_text'].strip()) or '-->' in sub['original_text']:
                i += 1
                continue
            
            print(f"\n--- Line {i+1}/{len(subtitles)} ---")
            print(f"Time: {sub['timing']}")
            print(f"English: {sub['original_text']}")
            print(f"Myanmar: {sub['translated_text']}")
            
            print("\nOptions:")
            print("1. ✅ Accept and continue")
            print("2. ✏️  Edit translation")
            print("3. ⏭️  Skip to next")
            print("4. ⏮️  Go back")
            print("5. 🏁 Finish review")
            
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == '1':
                i += 1
            elif choice == '2':
                new_translation = input("Enter new translation: ").strip()
                if new_translation:
                    sub['translated_text'] = new_translation
                    self.translation_memory[sub['original_text']] = new_translation
                i += 1
            elif choice == '3':
                i += 1
            elif choice == '4':
                i = max(0, i - 1)
            elif choice == '5':
                break
            else:
                print("Invalid choice, continuing...")
                i += 1
        
        self.save_memory()
    
    def show_statistics(self, subtitles):
        """Show translation statistics"""
        total_lines = len([s for s in subtitles if not re.match(r'^\d+$', s['original_text'].strip()) and '-->' not in s['original_text'])])
        translated_lines = len([s for s in subtitles if s['translated_text']])
        
        print(f"\n📊 Translation Statistics:")
        print(f"Total lines: {total_lines}")
        print(f"Translated lines: {translated_lines}")
        print(f"Progress: {(translated_lines/total_lines)*100:.1f}%")
        print(f"Memory entries: {len(self.translation_memory)}")

def main():
    """Main function"""
    translator = SubtitleTranslator()
    
    print("🎌 Myanmar Subtitle Translator")
    print("="*40)
    
    while True:
        print("\nMain Menu:")
        print("1. 📁 Translate SRT file")
        print("2. 📊 View statistics")
        print("3. 🧹 Clear memory")
        print("4. 🚪 Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            # File translation workflow
            file_path = input("Enter SRT file path: ").strip()
            
            if not os.path.exists(file_path):
                print("❌ File not found!")
                continue
            
            # Parse SRT
            subtitles = translator.parse_srt(file_path)
            print(f"📄 Loaded {len(subtitles)} subtitle blocks")
            
            # Auto-translate
            subtitles = translator.auto_translate_all(subtitles)
            
            # Interactive review
            review = input("Start interactive review? (y/n): ").strip().lower()
            if review == 'y':
                translator.interactive_review(subtitles)
            
            # Export
            output_path = input("Enter output file path (or press Enter for 'translated.srt'): ").strip()
            if not output_path:
                output_path = 'translated.srt'
            
            translator.export_srt(subtitles, output_path)
            print(f"✅ Exported to {output_path}")
            
            # Save memory
            translator.save_memory()
            
        elif choice == '2':
            translator.show_statistics([])
            print(f"Translation memory entries: {len(translator.translation_memory)}")
            
        elif choice == '3':
            confirm = input("Clear all translation memory? (y/n): ").strip().lower()
            if confirm == 'y':
                translator.translation_memory = {}
                translator.save_memory()
                print("✅ Memory cleared!")
                
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
