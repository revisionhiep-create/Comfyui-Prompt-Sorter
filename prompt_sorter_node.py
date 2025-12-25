import logging

logger = logging.getLogger(__name__)

# --- COMPREHENSIVE DANBOORU CATEGORIES ---
# We use broad "Root Words" to catch thousands of variations.
CATEGORIES = {
    "subjects": {
        "priority": 10, 
        "keywords": [
            "1boy", "1girl", "2boys", "2girls", "multiple", "solo", "hetero", "yuri", "yaoi", "threesome", "foursome", "group", 
            "character", "man", "woman", "guy", "lady", "boy", "girl", "male", "female", "couple"
        ]
    },
    "scene_env": {
        "priority": 20, 
        "keywords": [
            "outdoors", "indoors", "classroom", "forest", "beach", "cityscape", "underwater", "room", "sky", "background",
            "mountain", "ocean", "sea", "street", "building", "house", "garden", "park", "office", "bedroom", "kitchen",
            "night", "day", "sunset", "sunrise", "weather", "rain", "snow", "cloudy", "sunny", "nature", "scenery", "landscape"
        ]
    },
    "character_traits": {
        "priority": 30, 
        "keywords": [
            "hair", "eyes", "skin", "blush", "freckles", "mature", "milf", "shota", "loli", "age", "body", "physique",
            "breast", "thigh", "leg", "arm", "hand", "face", "expression", "smile", "grin", "angry", "sad", "crying",
            "horn", "wing", "tail", "ear", "animal_ears", "makeup", "lipstick", "tattoo", "scar"
        ]
    },
    "clothing_accessories": {
        "priority": 40, 
        "keywords": [
            "uniform", "dress", "bikini", "suit", "jacket", "hoodie", "skirt", "thighhighs", "glasses", "hat", "clothing", 
            "sweater", "shorts", "pants", "jeans", "shirt", "top", "bottom", "shoe", "boot", "sock", "glove", "necktie",
            "ribbon", "belt", "armor", "costume", "outfit", "jewelry", "necklace", "earring", "bracelet", "cape", "cloak"
        ]
    },
    "action_pose": {
        "priority": 50, 
        "keywords": [
            "standing", "sitting", "lying", "squatting", "kneeling", "pose", "stance", "sign", "holding", "stretching", 
            "leaning", "jumping", "running", "looking at viewer", "action", "movement", "walking", "dancing", "flying",
            "fighting", "hugging", "kissing", "hand_on", "arm_up", "leg_up"
        ]
    },
    "style_quality": {
        "priority": 60, 
        "keywords": [
            "masterpiece", "best quality", "aesthetic", "absurdres", "highres", "8k", "hdr", "score_", "anime", "manga", 
            "illustration", "detailed", "quality", "style", "art", "artstyle", "painting", "sketch", "digital", "traditional",
            "lighting", "shadow", "resolution", "rendering", "unreal", "unity"
        ]
    }
}

class IllustriousPromptSorter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sorted_text",)
    FUNCTION = "sort_prompt"
    CATEGORY = "utils"

    def sort_prompt(self, text):
        # 1. Clean, split by comma, and deduplicate
        raw_tags = [t.strip() for t in text.split(',') if t.strip()]
        seen = set()
        tags = []
        for t in raw_tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                tags.append(t)

        # 2. Bucket Sort
        buckets = {p["priority"]: [] for p in CATEGORIES.values()}
        buckets[100] = [] # Miscellaneous (Catch-all)
        lora_tags = []

        for tag in tags:
            if tag.startswith("<lora:") or tag.startswith("lora:"):
                lora_tags.append(tag)
                continue

            tag_lower = tag.lower().replace("_", " ") # Normalize underscores for matching
            found = False
            for cat_name, data in CATEGORIES.items():
                if any(kw in tag_lower for kw in data["keywords"]):
                    buckets[data["priority"]].append(tag)
                    found = True
                    break
            
            if not found:
                buckets[100].append(tag)

        # 3. Assemble
        final_list = []
        for p in sorted(buckets.keys()):
            # Within each bucket, we keep the original relative order
            final_list.extend(buckets[p])
        
        # LoRAs always at the end
        final_list.extend(lora_tags)

        return (", ".join(final_list),)

NODE_CLASS_MAPPINGS = {"IllustriousPromptSorter": IllustriousPromptSorter}
NODE_DISPLAY_NAME_MAPPINGS = {"IllustriousPromptSorter": "Illustrious Prompt Sorter 🛠️"}
