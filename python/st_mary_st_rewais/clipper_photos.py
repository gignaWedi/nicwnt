import json
import pyperclip

with open("python/st_mary_st_rewais/gallery.json") as file:
    data = json.load(file)

    for galleryname, gal_data in data.items():
        if "photos" not in gal_data:
            print(f"Skipping {galleryname} b/c no photos")
            input("ETC")
            continue
        
        print("==== STARTING A NEW GALLERY ====")
        print(galleryname)
        pyperclip.copy(galleryname)
        input("Press Enter to continue")

        photo_count = len(gal_data['photos'])
        print(f"Photos ({photo_count}):")
        for i, photo in enumerate(gal_data["photos"], 1):
            print(f"{i:3d}: {photo}")
            pyperclip.copy(photo)
            input("ETC")

        print()
