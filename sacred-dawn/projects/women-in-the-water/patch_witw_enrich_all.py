#!/usr/bin/env python3
"""patch_witw_enrich_all.py

Pass-1 whole-film enrichment (women-in-the-water). Lifts under-filled beats to
the ~11-word fill line (measured Elliot 156 WPM: 11 words ~= 4.2s in a 5.0s beat)
by developing each beat's OWN visual referent. Frozen: phenomenon, beat count,
order, sentence groups. narration is the only column touched.

Keyed on (block_id, clip_index). Anchor-verified: each edit matches the beat's
EXACT current narration before writing; ANY mismatch aborts the whole run with
the offending beats named (no partial writes). Beats already at the fill line are
listed with new == old (no-op). Idempotent, .pre_ backup once, ASCII-only, pure
stdlib, LAPTOP-side.

    cd ~/Projects/Pipeline
    python3 sacred-dawn/projects/women-in-the-water/patch_witw_enrich_all.py
"""
import argparse
import csv
import io
import os
import sys

# (block, clip): (OLD exact narration, NEW enriched narration)
EDITS = {
    # ---------------- BLOCK 1 ----------------
    (1,1):  ("There is a book most Bibles do not carry -", "There is a single ancient book most Bibles do not carry -"),
    (1,2):  ("a book the ancient world once knew by heart.", "a book the whole ancient world once knew, and lived by."),
    (1,3):  ("Its pages are Geez, the old tongue of Ethiopia -", "Its pages are written in Geez, the ancient tongue of the Ethiopian highlands -"),
    (1,4):  ("kept alive by hand for a thousand years.", "kept alive by hand, in that high place, for a thousand years."),
    (1,5):  ("The name on it is Enoch -", "The name the book carries is that of a single man - Enoch -"),
    (1,6):  ("the man Genesis says walked with God, and then was gone.", "the man Genesis says walked with God, and then was gone."),
    (1,7):  ("For centuries, the rest of the world let it vanish -", "For centuries after, the rest of the world let it vanish -"),
    (1,8):  ("buried, forgotten, cut from the canon we carry now.", "buried, forgotten, and quietly cut from the canon we still carry now."),
    (1,9):  ("Only one church kept it breathing -", "Only one distant church, high on its cliff, kept it breathing -"),
    (1,10): ("the Ethiopian Orthodox, who call it scripture to this day.", "the Ethiopian Orthodox Church, who call it scripture to this day."),
    (1,11): ("And here the story turns strange -", "And here - like a storm on the horizon - the story turns strange -"),
    (1,12): ("because the New Testament quotes it anyway.", "because the New Testament itself reaches back and quotes it anyway."),
    (1,13): ("In one short letter, Jude borrows a line from Enoch -", "In one short New Testament letter, Jude borrows a line from Enoch -"),
    (1,14): ("and never once pauses to explain himself.", "and never once pauses to explain himself, as if none was needed."),
    (1,15): ("So the early church knew this book -", "So the early church knew this book from the beginning -"),
    (1,16): ("knew it well enough to weave its words in their own.", "knew it well enough to weave its words in their own."),
    (1,17): ("Which leaves one question over everything -", "And it leaves one towering question standing over everything that follows -"),
    (1,18): ("why was a book this trusted ever buried?", "why was a book this trusted ever buried and left in the dark?"),
    (1,19): ("Look at the sixth chapter of Genesis -", "Look closely at the sixth chapter of the book of Genesis -"),
    (1,20): ("and you find the wound this book was written to close.", "and you find the wound this book was written to close."),
    (1,21): ("The sons of God, it says, took wives -", "The sons of God, the text says, came down and took wives -"),
    (1,22): ("and giants were born to them, the men of renown.", "and giants were born to them - the mighty men of renown."),
    (1,23): ("And then, mid-story, Genesis simply stops -", "And then, right in the middle of the story, Genesis simply stops -"),
    (1,24): ("as if you were meant to already know the rest.", "as if you were somehow meant to already know the rest."),
    (1,25): ("Enoch is where the rest was written down -", "The book of Enoch is where the rest was finally written down -"),
    (1,26): ("the account Genesis only brushes past in a verse.", "the whole account that Genesis only brushes past in a single verse."),
    (1,27): ("It opens a whole world before the flood -", "It opens up an entire lost world from before the flood -"),
    (1,28): ("vast, ancient, and tilting toward something terrible.", "a vast and ancient world, already tilting toward something truly terrible."),
    (1,29): ("And the old text says the ruin did not stop -", "And the old text says the ruin did not stop there -"),
    (1,30): ("not with the giants, and not even on dry land.", "not with the giants, and not even on the dry land."),
    (1,31): ("It reached the beasts, the birds -", "It reached the beasts of the field and the birds of the air -"),
    (1,32): ("the things that creep, and the things that swim.", "the things that creep upon the ground, and the things that swim below."),
    (1,33): ("Hold on to that last one -", "Hold on tightly to that very last one, just for now -"),
    (1,34): ("the things that swim - because almost no one tells it.", "the things that swim - because almost no one ever tells it."),
    (1,35): ("For now, hold on to what it opens -", "For now, simply hold on to what this book opens up -"),
    (1,36): ("because Enoch does not begin where you expect.", "because the book of Enoch does not begin at all where you expect."),
    (1,37): ("It does not begin at the flood -", "It does not begin with the flood, or with any water at all -"),
    (1,38): ("and it does not begin in any city of men.", "and it does not begin inside any city built by men."),
    (1,39): ("The account begins high on a mountain -", "The account begins high up on a cold and distant mountain -"),
    (1,40): ("where, the book says, two hundred of them came down.", "where, the book says, two hundred of them once came down."),
    # ---------------- BLOCK 2 ----------------
    (2,1):  ("Two hundred of them stood on the summit -", "Two hundred of them stood ranged across the high snow summit -"),
    (2,2):  ("the book calls them Watchers.", "the old book calls them the Watchers - vast and winged and terrible."),
    (2,3):  ("They were not sent - they chose to come down.", "They were not sent down - they chose to come down themselves."),
    (2,4):  ("And before they moved, they made a pact.", "And before they moved at all, they gathered and made a pact."),
    (2,5):  ("An oath, the old text says - binding each to all -", "An oath, the old text says - one binding each of them to all -"),
    (2,6):  ("so that not one of them could ever turn back.", "so that not a single one of them could ever turn back."),
    (2,7):  ("They swore it on the mountain itself -", "They swore it upon the cold mountain itself, beneath the open sky -"),
    (2,8):  ("and the mountain still carries the name of the oath.", "and the mountain still carries the very name of that oath."),
    (2,9):  ("This is Hermon - the highest peak of the old border -", "This is Hermon - the highest peak of the entire old border -"),
    (2,10): ("snow-crowned, watching over the whole land below.", "snow-crowned, and watching over the whole warm land far below."),
    (2,11): ("From its slopes, a river runs the length of scripture -", "From its slopes, a single river runs the length of scripture -"),
    (2,12): ("and here, the text says, the corruption entered the world.", "and here, the text says, the corruption first entered the world."),
    (2,13): ("They took human wives, the account says -", "They came down and took human wives, the account says -"),
    (2,14): ("and taught them things never meant for the earth.", "and taught them things that were never meant for the earth."),
    (2,15): ("Metal and blade, the old book says -", "Metal and blade and forge-fire, the old book plainly says -"),
    (2,16): ("and secrets the sky was never supposed to give.", "and secrets the sky above was never supposed to give them."),
    (2,17): ("And from those unions, the giants were born -", "And from those forbidden unions, the first giants were born -"),
    (2,18): ("the men of renown, the account calls them.", "the mighty men of renown, the old account calls them."),
    (2,19): ("They grew beyond anything the earth could feed -", "They grew beyond anything the whole earth could ever feed -"),
    (2,20): ("and when the food ran out, they turned on it.", "and when the food ran out at last, they turned on it."),
    (2,21): ("The whole world tilted into violence -", "And so the whole world tilted down into open violence -"),
    (2,22): ("exactly the word Genesis reaches for next.", "and that is exactly the word the book of Genesis reaches for next."),
    (2,23): ("And the ruin, the book insists, did not stay on land -", "And the ruin, the book insists, did not stay on land -"),
    (2,24): ("it reached the beasts, the birds, the deep.", "it reached the beasts, the birds, and the deep sea itself."),
    (2,25): ("Now hold the question the account never answers -", "Now hold on to the question the account never once answers -"),
    (2,26): ("the giants were sons - the men of renown.", "the giants were all sons - the mighty men of renown."),
    (2,27): ("But if sons were born, daughters were born too -", "But if the sons were born, then daughters were born too -"),
    (2,28): ("and the old texts spend almost no words on them.", "and yet the old texts spend almost no words on them."),
    (2,29): ("Genesis names the warriors, the powerful -", "Genesis names only the warriors, the mighty and the powerful -"),
    (2,30): ("and lets the daughters slip out of the story.", "and it lets the daughters slip quietly out of the story."),
    (2,31): ("So what became of them?", "So what became of them - the daughters lost to the water?"),
    (2,32): ("If the sons became giants of the land -", "If the sons among them became the giants of the land -"),
    (2,33): ("what did the daughters become in the water?", "what, then, did the daughters become down in the water?"),
    (2,34): ("Hold that thread - it runs the whole world through.", "Hold on to that thread - it runs the whole world through."),
    (2,35): ("Because the flood, when it came, judged the land -", "Because the flood, when at last it came, judged the land -"),
    (2,36): ("everything that breathed air and walked was swept away.", "everything that breathed the air and walked upon it was swept away."),
    (2,37): ("But water does not drown what already lives in water -", "But water does not drown what already lives within the water -"),
    (2,38): ("the sea was never threatened - the sea was its home.", "the sea was never threatened - the sea was its own home."),
    (2,39): ("And every ocean on earth remembers something -", "And every ocean on the earth remembers something of her -"),
    (2,40): ("the same woman, in a hundred different tongues.", "the same single woman, remembered in a hundred different tongues."),
    # ---------------- BLOCK 3 ----------------
    (3,1):  ("Every ocean on earth remembers the same woman -", "Every ocean on the whole earth remembers the very same woman -"),
    (3,2):  ("and no one can agree how that happened.", "and no one alive can agree on how that ever happened."),
    (3,3):  ("Peoples who never met, oceans they could not cross -", "Distant peoples who never met, over oceans they could not cross -"),
    (3,4):  ("drew the very same figure in the water.", "each drew the very same figure rising out of the water."),
    (3,5):  ("To know what she is, go back before the flood -", "To know what she is, go back before the flood -"),
    (3,6):  ("to the ruin the old book says spread everywhere.", "to the ruin the old book says had spread everywhere."),
    (3,7):  ("The corruption, Enoch says, did not stay in the bloodline -", "The corruption, Enoch says, did not stay in the bloodline -"),
    (3,8):  ("it reached the beasts, the birds, the things that creep -", "it reached the beasts, the birds, the things that creep -"),
    (3,9):  ("and the account adds three words most retellings skip -", "and the account adds three short words most retellings skip -"),
    (3,10): ("the things that swim.", "the things, the account says, that swim in the black water."),
    (3,11): ("Then the flood came, the book says -", "Then the flood came at last, just as the book says -"),
    (3,12): ("and swept the land clean of what walked it.", "and swept the whole land clean of all that walked it."),
    (3,13): ("But a flood judges the land - never the deep -", "But a flood judges the land - it never judges the deep -"),
    (3,14): ("the sea does not drown what already lives in it.", "the sea does not drown what already lives in it."),
    (3,15): ("So the old book leaves a gap it never closes -", "So the old book leaves a gap it never closes -"),
    (3,16): ("a corruption in the water, and a judgment that missed it.", "a corruption in the water, and a judgment that missed it."),
    (3,17): ("And in that gap, the daughters return -", "And in that open gap, the lost daughters at last return -"),
    (3,18): ("the ones the account let slip away.", "the very ones the old account had let slip quietly away."),
    (3,19): ("Because the sons became giants of the land -", "Because the sons of the Watchers became giants of the land -"),
    (3,20): ("and something, the legends say, rose in the water.", "and something, the old legends say, rose up in the water."),
    (3,21): ("Begin with the oldest - the Greek sirens -", "Begin with the very oldest of them all - the Greek sirens -"),
    (3,22): ("and throw out the picture the movies gave you.", "and throw out entirely the picture that the movies gave you."),
    (3,23): ("The first sirens had no fish tail at all -", "The earliest sirens of all had no fish tail at all -"),
    (3,24): ("they were women with the wings and talons of a bird.", "they were women with the wings and talons of a bird."),
    (3,25): ("One thing never changed across a thousand years -", "One thing alone never changed across the long thousand years -"),
    (3,26): ("not the shape of her, but the voice.", "not the shape of her at all, but always the voice."),
    (3,27): ("Homer wrote it plainly - the song was a weapon -", "Homer himself wrote it plainly - the song was a weapon -"),
    (3,28): ("and every sailor who heard it lost his will.", "and every last sailor who heard it lost all his will."),
    (3,29): ("They steered for the music until the hull broke -", "They steered straight for the music until the hull broke apart -"),
    (3,30): ("a beauty that ended in the water, every time.", "a fatal beauty that ended down in the water, every time."),
    (3,31): ("Then cross the world to West Africa -", "Then cross the entire world to the coast of West Africa -"),
    (3,32): ("where she is called Mami Wata - mother water.", "where she is called Mami Wata - the very mother of water."),
    (3,33): ("Beautiful, the traditions say - and never safe -", "Beautiful, the old traditions say - and yet never once safe -"),
    (3,34): ("she draws men down into a world not their own.", "she draws men down into a world not their own."),
    (3,35): ("And her cult is no small thing -", "And her cult, even now, is truly no small thing -"),
    (3,36): ("it runs a whole continent, and crossed the sea.", "it runs across a whole continent, and even crossed the sea."),
    (3,37): ("Two peoples, two oceans, one impossible woman -", "Two separate peoples, two far oceans, one impossible woman between them -"),
    (3,38): ("and the pattern, we will see, has only begun.", "and the pattern, as we will see, has only just begun."),
    (3,39): ("How does the whole world keep the same memory?", "How does the whole wide world keep the very same memory?"),
    (3,40): ("The answer runs straight back to that mountain.", "The answer, it turns out, runs straight back to that mountain."),
    # ---------------- BLOCK 4 ----------------
    (4,1):  ("She is not only Greek, and not only African -", "She is not only Greek, and not only African at all -"),
    (4,2):  ("the same figure waits on almost every map.", "the exact same figure waits on almost every map we have."),
    (4,3):  ("Go to Mesopotamia - the cradle itself -", "Go now to Mesopotamia - the ancient cradle of the world itself -"),
    (4,4):  ("the very ground where Genesis begins its story.", "the very ground where the book of Genesis begins its story."),
    (4,5):  ("The Babylonians carved her into their walls -", "The Babylonians carved her image deep into their ancient walls -"),
    (4,6):  ("half woman, half fish, from before the flood.", "half a woman and half a fish, from before the flood."),
    (4,7):  ("A being they called Oannes rose from the sea -", "A being they called Oannes rose up out of the sea -"),
    (4,8):  ("and taught mankind knowledge it was never given.", "and taught all mankind knowledge it was never meant to have."),
    (4,9):  ("And the echo is impossible to miss -", "And the echo here is simply impossible to miss at all -"),
    (4,10): ("for Enoch says the Watchers taught the very same.", "for Enoch says the Watchers taught humankind the very same things."),
    (4,11): ("The oldest mermaid of all was Syrian -", "The very oldest mermaid of them all was, in fact, Syrian -"),
    (4,12): ("a goddess carved in stone and given worship.", "a full goddess carved in stone and given real worship there."),
    (4,13): ("This is not the edge of the map inventing a tale -", "This is not the edge of the map inventing a tale -"),
    (4,14): ("it is the center of the biblical world itself.", "it is the very heart and center of the biblical world."),
    (4,15): ("And past all reason, the pattern keeps spreading -", "And past all reason at all, the pattern just keeps spreading -"),
    (4,16): ("to peoples who never heard of Homer.", "out to far peoples who had never heard the name Homer."),
    (4,17): ("In the Amazon she is the Iara -", "Far in the Amazon, they know her as the Iara -"),
    (4,18): ("mother of the water, whose song draws men down.", "the mother of the water, whose song draws men down."),
    (4,19): ("In the Slavic rivers, the Rusalka -", "In the cold Slavic rivers, they know her as the Rusalka -"),
    (4,20): ("a woman of deadly beauty in the water.", "a woman of deadly, luring beauty, waiting there in the water."),
    (4,21): ("In Japan, the Ningyo - a fish-woman -", "In far Japan, they tell of the Ningyo - a fish-woman -"),
    (4,22): ("written of a thousand years ago.", "and first written of there, in Japan, a thousand years ago."),
    (4,23): ("On the cold coasts of Ireland, the Selkie -", "On the cold, wet coasts of Ireland, there is the Selkie -"),
    (4,24): ("who sheds her sealskin and walks as a woman.", "who sheds her grey sealskin and walks ashore as a woman."),
    (4,25): ("Always drawn back to the sea -", "But she is always drawn back again to the sea -"),
    (4,26): ("always leaving the land behind her.", "and always, in the end, leaving the land behind her."),
    (4,27): ("Every continent, every ocean, every age -", "On every continent, in every ocean, in every single age -"),
    (4,28): ("arriving at the very same woman.", "and all arriving, in the end, at the very same woman."),
    (4,29): ("Feminine, and far more than human -", "She is feminine, and yet far more than merely human at all -"),
    (4,30): ("tied to the deep water - and always the voice.", "tied always to the deep water - and always the voice."),
    (4,31): ("Two witnesses agreeing is a coincidence -", "Two lone witnesses agreeing on it is only a coincidence -"),
    (4,32): ("a hundred agreeing is something else entirely.", "but a full hundred of them agreeing is something else entirely."),
    (4,33): ("They never traded, never met -", "These peoples never traded, and they had never once met -"),
    (4,34): ("yet drew the same creature down to the details.", "yet each drew the same creature down to the smallest details."),
    (4,35): ("A myth drifts - it shifts with every telling -", "A myth always drifts - it shifts a little with every telling -"),
    (4,36): ("but this one barely moves across the world.", "but this single one barely moves at all across the world."),
    (4,37): ("That, some who study this say, is the line -", "That, some who study this closely say, is the line -"),
    (4,38): ("the line between a myth and a memory.", "the fine line between a mere myth and a real memory."),
    (4,39): ("And a memory, they say, keeps its shape -", "And a real memory, they say, holds fast to its shape -"),
    (4,40): ("because it is remembering something that was real.", "because it is remembering something that had really once been real."),
    # ---------------- BLOCK 5 ----------------
    (5,1):  ("Before we go further, the skeptic deserves his say -", "Before we go any further, the skeptic deserves his say -"),
    (5,2):  ("and not the lazy version - the strongest one there is.", "and not the lazy version - the strongest one there is."),
    (5,3):  ("The easy answer is that people simply share the same fears -", "The easy answer is that people simply share the same fears -"),
    (5,4):  ("water is dangerous, and beauty is distracting.", "water is deeply dangerous, and beauty is always distracting to men."),
    (5,5):  ("Put those two together, the argument runs -", "Put those two simple fears together, and the argument runs on -"),
    (5,6):  ("and any people might dream up a deadly woman in the sea.", "and any people might dream up a deadly woman in the sea."),
    (5,7):  ("It is a serious answer - and it explains the frame -", "It is a serious answer - and it explains the frame -"),
    (5,8):  ("but it strains against the detail.", "but it strains hard against the detail once you truly examine it."),
    (5,9):  ("A shared fear can explain a vague resemblance -", "A shared fear could explain a vague and general resemblance between them -"),
    (5,10): ("it cannot explain the same woman, down to the details.", "it cannot explain the same woman, down to the details."),
    (5,11): ("The voice as a weapon - not just a pretty sound -", "The voice as a weapon - not just a pretty sound -"),
    (5,12): ("the pull that overrides a man, instead of tempting him.", "the pull that overrides a man, instead of tempting him."),
    (5,13): ("The link to the deep sea - not a lake, not the rain -", "The link to the deep sea - not a lake, not the rain -"),
    (5,14): ("and a fate that is fatal, every single time.", "and a fate that is fatal, every single time, without fail."),
    (5,15): ("Then comes the deepest version of the skeptic's case -", "Then comes the very deepest version of the skeptic's case -"),
    (5,16): ("and it needs no watchers and no giants at all.", "and it needs no watchers and no giants at all."),
    (5,17): ("The mind, it says, carries its own inherited shapes -", "The human mind, it says, carries its own inherited shapes -"),
    (5,18): ("molds every human is born already holding.", "deep molds that every one of us is born already holding."),
    (5,19): ("On this view she rises from within, not from the sea -", "On this view she rises from within, not from the sea -"),
    (5,20): ("the feminine that draws and threatens, joined to the deep.", "the feminine that draws and threatens, joined to the deep."),
    (5,21): ("By that logic any people would draw her -", "By that same logic, any people at all would draw her -"),
    (5,22): ("not because they saw her - because they carry her.", "not because they ever saw her - but because they carry her."),
    (5,23): ("It is an elegant answer, and an honest one -", "It is an elegant answer, and an honest one too -"),
    (5,24): ("and it would be dishonest to wave it away.", "and it would be truly dishonest to just wave it away."),
    (5,25): ("But it too strains where the detail is sharpest -", "But it, too, strains right where the detail is sharpest -"),
    (5,26): ("the voice, the deep water, the fate that never varies.", "the voice, the deep water, the fate that never varies."),
    (5,27): ("The archetype explains the frame around her -", "The archetype explains the wide frame that is drawn around her -"),
    (5,28): ("but not the precision of the picture inside it.", "but not the fine precision of the picture inside it."),
    (5,29): ("We will not pretend either side is proven -", "We will not pretend that either side has been fully proven -"),
    (5,30): ("only watch where each is strong, and where each strains.", "only watch where each is strong, and where each strains."),
    (5,31): ("And if it is a memory - a memory of what?", "And if it is a memory - a memory of what?"),
    (5,32): ("the question runs straight back before the flood.", "and the question runs straight back to before the flood itself."),
    (5,33): ("To the one old book that treats her as real -", "To the one old book that treats her as real -"),
    (5,34): ("not as poetry, but as something that happened.", "not as poetry at all, but as something that truly happened."),
    (5,35): ("And the answer, it turns out, is hidden in the words -", "And the answer, it turns out, is hidden in the words -"),
    (5,36): ("in a handful the old translators could not agree on.", "in a handful the old translators could not agree on."),
    (5,37): ("One word the ancients reached for meant a hybrid thing -", "One word the ancients reached for meant a hybrid thing -"),
    (5,38): ("a being that was never fully of this world.", "a strange being that was never quite fully of this world."),
    (5,39): ("And it appears where the land lies cursed and empty -", "And it appears where the land lies cursed and empty -"),
    (5,40): ("where only what is not fully human remains.", "where only the things that are not fully human still remain."),
    # ---------------- BLOCK 6 ----------------
    (6,1):  ("The clue was never in the stories - it was in the words -", "The clue was never in the stories - it was in the words -"),
    (6,2):  ("in a handful the old translators could never pin down.", "in a handful the old translators could never pin down."),
    (6,3):  ("One appears in the prophet Isaiah - the word lilit -", "One of them appears in the prophet Isaiah - the word lilit -"),
    (6,4):  ("and the translations scatter in every direction.", "and from that single word the translations scatter in every direction."),
    (6,5):  ("Some render it owl, some a night creature -", "Some render it as owl, and some as a night creature -"),
    (6,6):  ("others simply gave up and left it untranslated.", "while others just gave up and left it wholly untranslated there."),
    (6,7):  ("But the oldest Greek version chose a different word -", "But the very oldest Greek version chose a different word -"),
    (6,8):  ("it called her a hybrid - half one thing, half another.", "it called her a hybrid - half one thing, half another."),
    (6,9):  ("And read where the prophet sets her -", "And read closely just where the prophet actually sets her down -"),
    (6,10): ("in a cursed and emptied land, after the judgment.", "in a cursed and emptied land, long after the judgment."),
    (6,11): ("Where only what is not fully human remains -", "Where only the things not fully human are left to remain -"),
    (6,12): ("that, the text says, is where she dwells.", "that, the old text plainly says, is where she now dwells."),
    (6,13): ("Around that one word, a whole figure grew -", "And around that single word, a whole figure slowly grew up -"),
    (6,14): ("feminine, supernatural, tied to night and the deep.", "feminine, and supernatural, and tied to the night and the deep."),
    (6,15): ("Then a second word runs through the old text - tannin -", "Then a second word runs through the old text - tannin -"),
    (6,16): ("translated dragon in one place, sea monster in the next.", "translated dragon in one place, sea monster in the next."),
    (6,17): ("And here the point turns sharp -", "And here, at long last, is where the point turns sharp -"),
    (6,18): ("the flood judged the land, but the sea stayed beyond it.", "the flood judged the land, but the sea stayed beyond it."),
    (6,19): ("It is in the book of Job this gets its fullest voice -", "It is in the book of Job this gets its fullest voice -"),
    (6,20): ("where God himself describes the Leviathan.", "the place where God himself describes the great and vast Leviathan."),
    (6,21): ("A creature of the deep no weapon can wound -", "A creature of the deep that no weapon can wound -"),
    (6,22): ("that breathes fire, and dwells where light gives out.", "that breathes out fire, and dwells where all light gives out."),
    (6,23): ("And the most striking thing is who speaks of it -", "And the most striking thing is who speaks of it -"),
    (6,24): ("not a poet, but God, as a real and present thing.", "not a poet, but God, as a real and present thing."),
    (6,25): ("For the ancient writer, the sea was never just water -", "For the ancient writer, the sea was never just water -"),
    (6,26): ("it was the deep - the place order never fully reached.", "it was the deep - the place order never fully reached."),
    (6,27): ("Genesis says it in its second breath -", "The book of Genesis says it in its very second breath -"),
    (6,28): ("darkness over the face of the deep, before all else.", "darkness over the face of the deep, before all else."),
    (6,29): ("And other lines name a monster the sea still holds -", "And other lines name a monster the sea still holds -"),
    (6,30): ("a chaos the divine hand had to press back down.", "a chaos the divine hand had to press back down."),
    (6,31): ("The old world knew what lived in the deep places -", "The old world knew what lived in the deep places -"),
    (6,32): ("a knowledge we have lost almost entirely.", "a deep knowledge that we ourselves have since lost almost entirely."),
    (6,33): ("And they wrote it not as legend -", "And they wrote all of it down, not as mere legend -"),
    (6,34): ("but as fact, in the plainest words they had.", "but as sober fact, in the very plainest words they had."),
    (6,35): ("So the words themselves keep pointing one way -", "So the very words themselves keep pointing us all one way -"),
    (6,36): ("back to the deep, and to what the flood never touched.", "back to the deep, and to what the flood never touched."),
    (6,37): ("A corruption that reached the water -", "A corruption that had reached down, at last, into the water -"),
    (6,38): ("and a judgment that fell only on the land.", "and a judgment that fell only upon the dry land."),
    (6,39): ("Two facts, the old book leaves standing side by side -", "Two facts, the old book leaves standing side by side -"),
    (6,40): ("and in the space between them, she lives.", "and in the narrow space left between them, she still lives on."),
    # ---------------- BLOCK 7 ----------------
    (7,1):  ("Now set the whole thing in order -", "Now, at last, set the whole thing carefully in order -"),
    (7,2):  ("because it is when the picture lines up that it holds.", "because it is when the picture lines up that it holds."),
    (7,3):  ("The Watchers came down, drawn by human women -", "The Watchers first came down, all drawn down by human women -"),
    (7,4):  ("and from them the giants were born, the men of renown.", "and from them the giants were born, the men of renown."),
    (7,5):  ("But watch the shape of it - the symmetry -", "But now watch the strange shape of it - the symmetry itself -"),
    (7,6):  ("because the symmetry is the unsettling part.", "for the symmetry of it is the truly unsettling part of all."),
    (7,7):  ("The fathers came down, through the women -", "The great fathers came down, down through the human women below -"),
    (7,8):  ("a descent, out of the sky, into the world.", "a descent - down out of the sky, into the world."),
    (7,9):  ("And the reflection, the legends say, rose the other way -", "And the reflection, the legends say, rose the other way -"),
    (7,10): ("through the men - an ascent, out of the water.", "up through the men - an ascent, out of the water."),
    (7,11): ("The daughters carried the same nature as the sons -", "The daughters carried within them the same nature as the sons -"),
    (7,12): ("and turned it on men, as the sons turned it on the world.", "and turned it on men, as the sons turned it on the world."),
    (7,13): ("One came down through the sky -", "The one of them came down, down through the open sky -"),
    (7,14): ("the other rose up through the sea.", "and the other one rose up, up through the deep sea."),
    (7,15): ("The old book, remember, says the Bible does not close it -", "The old book, remember, says the Bible does not close it -"),
    (7,16): ("it names no verse that follows her into the deep.", "it names no verse that follows her into the deep."),
    (7,17): ("What it gives instead is a stranger fact -", "What it gives us instead is a far stranger fact indeed -"),
    (7,18): ("the flood was meant to end them - and did not.", "the flood was meant to end them - and did not."),
    (7,19): ("Because the giants come back - after the water -", "Because the giants themselves come back, even after the water -"),
    (7,20): ("whole peoples of them, with names and lands.", "whole peoples of them, each with their own names and lands."),
    (7,21): ("Moses' spies came back terrified -", "The spies that Moses sent came back utterly terrified of them -"),
    (7,22): ("we were as grasshoppers, they said, before them.", "we were as mere grasshoppers, they said, standing before them."),
    (7,23): ("And the plainest case the text records is a king -", "And the plainest case the text records is a king -"),
    (7,24): ("Og of Bashan, the last of a giant line.", "Og of Bashan - the very last of a giant line."),
    (7,25): ("The book does something almost forensic here -", "The old book does something here that is almost forensic in nature -"),
    (7,26): ("it records the size of his iron bed.", "it carefully records the sheer size of his great iron bed."),
    (7,27): ("More than four meters long -", "It stretched more than four whole meters in length, that bed -"),
    (7,28): ("as if a scribe wanted to prove it was no tale.", "as if a scribe wanted to prove it was no tale."),
    (7,29): ("And this is a thousand years after the flood -", "And this was a full thousand years after the great flood -"),
    (7,30): ("long after the water should have erased them all.", "long after the water should surely have erased them all."),
    (7,31): ("Somehow what should have vanished came back -", "Somehow, that which should have vanished had come back once more -"),
    (7,32): ("not as a legend, but as flesh, bone, and iron.", "not as a legend, but as flesh, bone, and iron."),
    (7,33): ("The text does not explain how -", "The old text does not even try to explain how at all -"),
    (7,34): ("it records it, and simply moves on.", "it simply records the plain fact, and then moves quietly on."),
    (7,35): ("Leaving the contradiction on the page -", "Leaving the plain contradiction sitting right there upon the page -"),
    (7,36): ("for anyone with the eyes to notice it.", "for anyone at all who has the eyes to notice it."),
    (7,37): ("If the sons survived the water on the land -", "If the sons somehow survived the water on the land -"),
    (7,38): ("what survived it, the legends ask, in the sea?", "then what survived it all, the legends ask, in the sea?"),
    (7,39): ("The story is nearly whole now -", "And now, at last, the story is very nearly whole -"),
    (7,40): ("and it ends, of all places, at the sea.", "and it ends, of all places, out at the sea."),
    # ---------------- BLOCK 8 ----------------
    (8,1):  ("The story is nearly whole - and it ends at the sea.", "The story is nearly whole - and it ends at the sea."),
    (8,2):  ("Turn to the very last book of the Bible.", "Turn now to the very last book of the whole Bible."),
    (8,3):  ("John writes of a new heaven and a new earth -", "John writes of a new heaven and a new earth -"),
    (8,4):  ("the first heaven and the first earth passed away.", "and the first heaven and the first earth had passed away."),
    (8,5):  ("And then he adds four words almost no one pauses on -", "And then he adds four words almost no one pauses on -"),
    (8,6):  ("and the sea was no more.", "and then he says it plainly - the sea was no more."),
    (8,7):  ("Of everything he could have named gone -", "Of every single thing he could have named as finally gone -"),
    (8,8):  ("no more death, no more pain, no more tears -", "no more death, no more pain, and no more tears -"),
    (8,9):  ("he makes a point of saying the sea is gone.", "he makes a point of saying the sea is gone."),
    (8,10): ("Why the sea? Why would that stand among the great promises?", "Why the sea? Why would that stand among the great promises?"),
    (8,11): ("Because in the old texts the sea was never only water -", "Because in the old texts the sea was never only water -"),
    (8,12): ("it was the deep, the abyss, the place order never reached.", "it was the deep, the abyss, the place order never reached."),
    (8,13): ("John writes it from exile, on an island -", "John himself writes it from exile, alone on a far island -"),
    (8,14): ("ringed on every side by the very sea he says will end.", "ringed on every side by the very sea he says will end."),
    (8,15): ("If the sea holds the memory of what came before -", "If the sea holds the memory of what came before -"),
    (8,16): ("then its ending is not weather, and not geography.", "then its ending is not weather, and not mere geography."),
    (8,17): ("It is a door, the old readers say, finally closing -", "It is a door, the old readers say, finally closing -"),
    (8,18): ("a door that stood open since the days of Noah.", "a door that stood open since the days of Noah."),
    (8,19): ("Since the Watchers, since the giants -", "Since the Watchers came, and since the giants themselves came -"),
    (8,20): ("since the daughters who went into the water.", "and since the daughters who all went down into the water."),
    (8,21): ("Since the sirens on their bright cliffs -", "Since the sirens who sang up on their bright sea-cliffs -"),
    (8,22): ("since Mami Wata, mother of the West African rivers -", "since Mami Wata, the mother of the West African rivers -"),
    (8,23): ("since Atargatis, carved in Syrian stone -", "since Atargatis, the goddess carved long ago in Syrian stone -"),
    (8,24): ("since Oannes, who rose to teach the Babylonians -", "since Oannes, who rose from the sea to teach the Babylonians -"),
    (8,25): ("since the Iara, singing on the Amazon -", "since the Iara, singing far out upon the great Amazon river -"),
    (8,26): ("since the Rusalka, and the Ningyo -", "since the pale Rusalka, and since the far-off Ningyo too -"),
    (8,27): ("since the Selkie on the cold bright coasts -", "since the Selkie out upon the cold and bright northern coasts -"),
    (8,28): ("the water spirits of a hundred cultures.", "the water spirits, all of them, of a hundred scattered cultures."),
    (8,29): ("A hundred peoples who never knew one another -", "A whole hundred peoples who had never once known one another -"),
    (8,30): ("who all remembered the very same woman.", "and who all, somehow, remembered the very same single woman."),
    (8,31): ("Feminine, and more than human -", "She is always feminine, and yet far more than merely human -"),
    (8,32): ("tied to the deep water - and always the voice.", "tied always to the deep water - and always the voice."),
    (8,33): ("We do not ask you to close the question -", "We do not ask you here to close the question -"),
    (8,34): ("only to feel the weight of what gathers, page by page.", "only to feel the weight of what gathers, page by page."),
    (8,35): ("The old texts describe her - we do not claim to prove her -", "The old texts describe her - we do not claim to prove her -"),
    (8,36): ("because an absent verse is not the same as absent evidence.", "because an absent verse is not the same as absent evidence."),
    (8,37): ("And what gathers, culture after culture, is hard to set down -", "And what gathers, culture after culture, is hard to set down -"),
    (8,38): ("the same woman, the same water, the same call.", "always the same woman, the same water, the same haunting call."),
    (8,39): ("The sea, John says, will one day be no more -", "The sea, John says, will one day be no more -"),
    (8,40): ("and this was only one of the things the buried book remembered.", "and this was only one of the things the buried book remembered."),
}


def repo_root(start):
    d = os.path.abspath(start)
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return None


def main():
    ap = argparse.ArgumentParser(description="whole-film pass-1 enrichment of WITW narration")
    ap.add_argument("--master", default=None)
    args = ap.parse_args()

    if args.master:
        path = os.path.abspath(args.master)
    else:
        root = repo_root(os.getcwd()) or repo_root(os.path.dirname(os.path.abspath(__file__)))
        if not root:
            sys.stderr.write("ERROR: no .git found walking up; pass --master PATH\n")
            sys.exit(1)
        path = os.path.join(root, "sacred-dawn", "projects", "women-in-the-water", "master.csv")

    if not os.path.isfile(path):
        sys.stderr.write("ERROR: master.csv not found: %s\n" % path)
        sys.exit(1)

    for pair in EDITS.values():
        for txt in pair:
            if any(ord(c) > 127 for c in txt):
                sys.stderr.write("ERROR: non-ASCII in edit text: %r\n" % txt)
                sys.exit(1)

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for col in ("narration", "block_id", "clip_index"):
        if col not in fieldnames:
            sys.stderr.write("ERROR: master.csv missing column %r\n" % col)
            sys.exit(1)

    changed, already, mismatched = [], [], []
    seen = set()
    for r in rows:
        key = (int(r["block_id"]), int(r["clip_index"]))
        if key not in EDITS:
            continue
        seen.add(key)
        old, new = EDITS[key]
        cur = r["narration"]
        if cur == new:
            already.append(key)
        elif cur == old:
            changed.append((key, r))
        else:
            mismatched.append((key, cur))

    if mismatched:
        sys.stderr.write("ERROR: anchor mismatch on %d beat(s) -- ABORT (no write):\n" % len(mismatched))
        for key, cur in mismatched:
            sys.stderr.write("  beat %d/%d current: %r\n" % (key[0], key[1], cur))
        sys.exit(1)

    missing = sorted(set(EDITS) - seen)
    if missing:
        sys.stderr.write("ERROR: EDITS beats not found in master: %s\n" % missing)
        sys.exit(1)

    if not changed:
        print("no change: all %d edited beats already current." % len(EDITS))
        return

    bak = path + ".pre_enrichall"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8", newline="") as f:
            f.write(open(path, "r", encoding="utf-8", newline="").read())
        print("backup: %s" % bak)

    for key, r in changed:
        r["narration"] = EDITS[key][1]

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    with open(path, "w", encoding="ascii", newline="") as f:
        f.write(buf.getvalue())

    print("OK: enriched %d beats (%d already current). master.csv rewritten."
          % (len(changed), len(already)))
    print("phenomenon / beat count / order all unchanged. Re-run audio then calibrate.")


if __name__ == "__main__":
    main()
