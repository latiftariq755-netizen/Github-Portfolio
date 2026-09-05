import random

# 1. Define your data pools
categories = {
    "Tech": {
        "hooks": ["You won't believe this new...", "Finally, the tool we needed:", "Stop doing this manually!"],
        "bodies": ["This AI tool is changing the game.", "Level up your workflow with this.", "This is a total lifesaver for devs."],
        "hashtags": ["#tech #coding #ai #innovation #python"]
    },
    "Education": {
        "hooks": ["Quick lesson on...", "Boost your grades with...", "The secret to understanding..."],
        "bodies": ["Let's break this down simply.", "Master this concept in 60 seconds.", "Study smarter, not harder."],
        "hashtags": ["#learning #students #stemma #education #tips"]
    },
    "Video Editing":{
        "hooks": ["Bring your creativity into editing...", "Video Editing is a power through which you can create anything you want."],
        "bodies": ["Only basic knowlege is enough to start editing...", "Master keyframe animation as a beginer"],
        "hashtags": ["#editing #visuals #motiongraphics #skill"]
    }
}

def generate_caption():
    print("--- Social Media Helper ---")
    print("Categories: Tech, Education, Video Editing")
    choice = input("Enter a category: ").title()

    if choice in categories:
        # 2. Logic to pick random elements
        hook = random.choice(categories[choice]["hooks"])
        body = random.choice(categories[choice]["bodies"])
        tags = random.choice(categories[choice]["hashtags"])

        # 3. Output the result
        print("\n--- Your Generated Caption ---")
        print(f"{hook}\n{body}\n\n{tags}")
    else:
        print("Category not found!")

generate_caption()