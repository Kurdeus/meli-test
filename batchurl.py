
import asyncio
import zipfile
import os
import re
import sys
import argparse
from pyppeteer import launch
from urllib.parse import urlparse





def sanitize_filename(name: str) -> str:
    """Remove invalid characters for filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)




async def save_mhtml(url: str, output_file: str):
    """Save webpage as MHTML."""
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url, waitUntil='networkidle0')
    mhtml_data = await page._client.send('Page.captureSnapshot', {})
    with open(output_file, 'wb') as f:
        f.write(mhtml_data['data'].encode())
    await browser.close()

def main(urls:str):


    for url in urls:
        base_name = sanitize_filename(url.split("/")[-1])


        mhtml_filename = f"{base_name}.mhtml"
        zip_filename = f"{base_name}.zip"

        # Create download directory
        download_dir = "download"
        os.makedirs(download_dir, exist_ok=True)

        # Temporary folder for MHTML
        os.makedirs("temp", exist_ok=True)
        mhtml_path = os.path.join("temp", mhtml_filename)

        asyncio.run(save_mhtml(url, mhtml_path))

        # Create ZIP inside download folder
        zip_path = os.path.join(download_dir, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write(mhtml_path, arcname=mhtml_filename)

        # Cleanup temp
        import shutil
        shutil.rmtree("temp", ignore_errors=True)

        print(f"✅ Created {zip_path} (contains {mhtml_filename})")

urls = """https://omegascans.org/series/kinkfolder-zip
https://omegascans.org/series/im-the-only-guy-at-the-massage-shop
https://omegascans.org/series/taming-my-stepsister
https://omegascans.org/series/ogh-reboot
https://omegascans.org/series/zealous-the-heretics-sabbath       
https://omegascans.org/series/love-quest
https://omegascans.org/series/money-games
https://omegascans.org/series/drunken-happenings-mahou-shoujo-lyrical-nanoha
https://omegascans.org/series/sugar-daddy
https://omegascans.org/series/i-want-to-work-quietly
https://omegascans.org/series/where-there-are-breasts-there-is-a-valley
https://omegascans.org/series/my-girlfriend-was-already-fully-trained
https://omegascans.org/series/like-father-like-son
https://omegascans.org/series/moms-and-daughter-in-a-big-mess
https://omegascans.org/series/ero-the-princess-submits
https://omegascans.org/series/mind-control
https://omegascans.org/series/im-a-vampire
https://omegascans.org/series/i-will-teach-you-self-defense
https://omegascans.org/series/when-my-huge-dicked-self-used-a-dating-app-and-met-a-super-perverted-woman-with-whom-i-have-the-best-compatibility        
https://omegascans.org/series/living-in-america""".splitlines()

if __name__ == "__main__":
    main(urls)
