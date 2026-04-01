"""
Seed script — populates the database with the existing hardcoded product data
from the original index.html so nothing is lost during the migration.

Run once:  python -m backend.seed
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, Base
from backend.models import Category, Product, Admin
from backend.auth import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Skip if already seeded
    if db.query(Category).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    # ── Categories ────────────────────────────────────────────────────────────
    cat_covers = Category(
        name="covers", display_name="Phone Cases",
        image_folder="covers", image_prefix="phonecover", image_ext=".jpg.jpeg",
        has_device_option=True, device_premium_label="iPhone / Samsung S series",
        device_premium_extra=50, sort_order=1,
    )
    cat_keychains = Category(
        name="keychains", display_name="Keychains",
        image_folder="keychains", image_prefix="keychain", image_ext=".jpg.jpeg",
        has_device_option=False, sort_order=2,
    )
    cat_hair = Category(
        name="hair-accessories", display_name="Hair Accessories",
        image_folder="hair acessories", image_prefix="hairclip", image_ext=".jpg.jpeg",
        has_device_option=False, sort_order=3,
    )
    cat_poshak = Category(
        name="poshak", display_name="Poshak",
        image_folder="poshaks", image_prefix="poshak", image_ext=".jpg.jpg",
        has_device_option=False, sort_order=4,
    )
    db.add_all([cat_covers, cat_keychains, cat_hair, cat_poshak])
    db.flush()  # get IDs

    # ── Phone Cases ───────────────────────────────────────────────────────────
    phone_cases = [
        (1, "Sweet Strawberry", 350), (2, "Daisy Mist", 250), (3, "Mulberry Mist", 250),
        (4, "Blue Blossom", 300), (5, "Cherry Mist", 250), (6, "Blooming Tulip", 300),
        (7, "Sky Mist", 250), (8, "Classic Bollywood", 300), (9, "Floral Classic", 300),
        (10, "Turtle Case", 300), (11, "Handmade Shell", 300), (12, "Pinky Bloom", 250),
        (13, "Bow Case", 250), (14, "Bunny Case", 300), (15, "Daisy Garden", 250),
        (17, "Mustard Bow", 270), (18, "Cozy Crochet", 300), (19, "Accorn Case", 300),
        (20, "Two Shades", 270), (21, "Bow Case", 270), (22, "Bunny Case 2", 300),
        (23, "Daisy Blossom", 250), (24, "Bow Case 2", 250), (25, "Panda Case", 300),
        (26, "Butterfly Case", 300), (27, "The Red Bunny", 300), (28, "The Cute Rabbit", 350),
        (29, "Bunny Case 3", 320), (30, "The Little Butterfly", 250), (31, "Standard Case", 300),
        (32, "Handmade Sheep", 270), (33, "Red Bow", 250), (34, "Bright Sunflower", 270),
        (35, "The Black Beauty", 250),
    ]
    for orig_id, name, price in phone_cases:
        db.add(Product(
            name=name, price=price, category_id=cat_covers.id,
            image_path=f"images/covers/phonecover{orig_id}.jpg.jpeg",
            sort_order=orig_id,
        ))

    # ── Keychains ─────────────────────────────────────────────────────────────
    keychains = [
        ("Sunny Daisy", 100), ("Evil eye with name letters", 200),
        ("Mochi octopus", 200), ("bean heart", 100), ("pink paw clouds", 100),
        ("camera keychain", 150), ("yummy cones", 150), ("red velvet bow", 120),
        ("misty star", 120), ("evil eye", 100), ("coco bear", 200),
        ("Daisy keychain", 100), ("misty star 2", 120), ("the balls", 150),
        ("shiny jelly fish", 220), ("bubblegum ghost", 150), ("rainbow", 150),
        ("purple star", 200), ("tulip pop", 220), ("football keychain", 150),
        ("the cricket key chains", 150), ("sky swirl tulip", 220),
        ("the sun , Earth", 200), ("capachino mug", 150), ("Dusty clouds", 100),
        ("Fancy cherries", 220), ("purple dino star", 200),
        ("the colour palette", 100), ("lilac heart with name initial.", 200),
        ("purple dino star", 200), ("flower keychain", 100),
    ]
    for idx, (name, price) in enumerate(keychains, 1):
        db.add(Product(
            name=name, price=price, category_id=cat_keychains.id,
            image_path=f"images/keychains/keychain{idx}.jpg.jpeg",
            sort_order=idx,
        ))

    # ── Hair Accessories ─────────────────────────────────────────────────────
    # IDs with size option: 6, 11, 21, 22, 23, 25, 29, 32
    size_option_ids = {6, 11, 21, 22, 23, 25, 29, 32}
    hair_items = [
        (1, "Flower clips (x2)", 80), (2, "Blue parandi", 120), (3, "Cherry", 100),
        (4, "Gajra", 250), (5, "Cute bows", 120), (6, "butterfly Clutcher", 120),
        (7, "White parandi", 120), (8, "Daisy", 100), (9, "Bow", 100),
        (10, "Daisy", 80), (11, "Flower Clutcher", 100), (12, "The Red Bow", 150),
        (13, "Bow 2", 100), (14, "Fancy Bow", 200), (15, "Flower clips (x2)", 50),
        (16, "Flower Rubberband", 80), (18, "Flower Hairpins", 100),
        (19, "Little Bow", 50), (20, "Bow rubberbands(x2)", 120),
        (21, "Bow Clutchers", 80), (22, "Flower clutcher2", 80),
        (23, "Rose clutcher", 150), (24, "Combo", 150),
        (25, "Flower Clutcher3", 100), (26, "Rose Rubberband", 100),
        (27, "Sunflower clutcher", 80), (28, "Scrunchie", 50),
        (29, "Tulip Clutcher", 150), (30, "Bow Clutcher", 100),
        (31, "red flower clutcher", 100), (32, "Sunflower clutcher", 150),
    ]
    for orig_id, name, price in hair_items:
        db.add(Product(
            name=name, price=price, category_id=cat_hair.id,
            image_path=f"images/hair acessories/hairclip{orig_id}.jpg.jpeg",
            has_size_option=(orig_id in size_option_ids),
            sort_order=orig_id,
        ))

    # ── Poshak ────────────────────────────────────────────────────────────────
    poshak_items = [
        (1, "Red&White poshak", 500), (2, "FLower poshak", 500),
    ]
    for orig_id, name, price in poshak_items:
        db.add(Product(
            name=name, price=price, category_id=cat_poshak.id,
            image_path=f"images/poshaks/poshak{orig_id}.jpg.jpg",
            sort_order=orig_id,
        ))

    # ── Default Admin ─────────────────────────────────────────────────────────
    db.add(Admin(username="admin", password_hash=hash_password("admin123")))

    db.commit()
    db.close()
    print("✅ Database seeded successfully!")
    print("   Admin login: admin / admin123")


if __name__ == "__main__":
    seed()
