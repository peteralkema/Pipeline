#!/usr/bin/env python3
"""patch_witw_enrich_pass2.py  --  Women in the Water, VO pass-2 enrichment.

Lifts 281 narration beats from ~10-11 words to 12-13 by folding in concrete
detail each beat's OWN phenomenon already shows (frozen: beat count, order,
sentence groups, phenomena, visuals -- only the narration WORDING changes).
Closes VO seams from ~-42s/block toward ~-22s/block (~13% air), the register
natural tolerance for this contemplative film -- NOT seams to zero (see G56).

Idempotent: a beat already at its pass-2 line is skipped. Anchor-verified: every
beat's CURRENT narration must equal the recorded pass-1 text, or the patch
ABORTS with no write. .pre_ backup once. ASCII-only. Operates on master.csv.

    cd ~/Projects/Pipeline/sacred-dawn/projects/women-in-the-water
    python3 patch_witw_enrich_pass2.py
"""
import argparse, csv, os, sys

EDITS = {
    (1,1): ('There is a single ancient book most Bibles do not carry -', 'There is a single ancient, leather-bound book most Bibles do not carry -'),
    (1,2): ('a book the whole ancient world once knew, and lived by.', 'a book the whole ancient world of towers once knew, and lived by.'),
    (1,6): ('the man Genesis says walked with God, and then was gone.', 'the man Genesis says walked with God - and then, like light, was gone.'),
    (1,7): ('For centuries after, the rest of the world let it vanish -', 'For centuries after, the rest of the world let it vanish into dust -'),
    (1,9): ('Only one distant church, high on its cliff, kept it breathing -', 'Only one distant church, blazing high on its dawn-lit cliff, kept it breathing -'),
    (1,10): ('the Ethiopian Orthodox Church, who call it scripture to this day.', 'the Ethiopian Orthodox Church, who still raise it and call it scripture today.'),
    (1,12): ('because the New Testament itself reaches back and quotes it anyway.', 'because the New Testament itself reaches back across time and quotes it anyway.'),
    (1,15): ('So the early church knew this book from the beginning -', 'So the early church knew this book from the very beginning of all -'),
    (1,16): ('knew it well enough to weave its words in their own.', 'knew it well enough to weave its very words into their own.'),
    (1,17): ('And it leaves one towering question standing over everything that follows -', 'And it leaves one towering question standing over everything else that follows -'),
    (1,19): ('Look closely at the sixth chapter of the book of Genesis -', 'Look closely now at the sixth chapter of the book of Genesis -'),
    (1,20): ('and you find the wound this book was written to close.', 'and there you find the wound this whole book was written to close.'),
    (1,22): ('and giants were born to them - the mighty men of renown.', 'and giants were born to them there - the mighty men of renown.'),
    (1,24): ('as if you were somehow meant to already know the rest.', 'as if you were somehow always meant to already know the rest.'),
    (1,27): ('It opens up an entire lost world from before the flood -', 'It opens up an entire lost world from long before the flood -'),
    (1,28): ('a vast and ancient world, already tilting toward something truly terrible.', 'a vast and ancient world, already tilting hard toward something truly terrible.'),
    (1,29): ('And the old text says the ruin did not stop there -', 'And the old text insists the ruin did not stop there at all -'),
    (1,30): ('not with the giants, and not even on the dry land.', 'not with the giants alone, and not even on the dry land.'),
    (1,33): ('Hold on tightly to that very last one, just for now -', 'Hold on tightly to that very last one of them, just for now -'),
    (1,34): ('the things that swim - because almost no one ever tells it.', 'the things that swim - because almost no one alive ever tells it.'),
    (1,35): ('For now, simply hold on to what this book opens up -', 'For now, simply hold tight to what this ancient book opens up -'),
    (1,38): ('and it does not begin inside any city built by men.', 'and it does not begin inside any walled city built by men.'),
    (1,39): ('The account begins high up on a cold and distant mountain -', 'The whole account begins high up on a cold and distant mountain -'),
    (1,40): ('where, the book says, two hundred of them once came down.', 'where, the old book says, two hundred of them once came down.'),
    (2,1): ('Two hundred of them stood ranged across the high snow summit -', 'Two hundred of them stood ranged there across the high, snow-locked summit -'),
    (2,3): ('They were not sent down - they chose to come down themselves.', 'They were not sent down at all - they chose to come down themselves.'),
    (2,8): ('and the mountain still carries the very name of that oath.', 'and the pale mountain still carries the very name of that oath.'),
    (2,9): ('This is Hermon - the highest peak of the entire old border -', 'This is Mount Hermon - the highest peak of the entire old border -'),
    (2,10): ('snow-crowned, and watching over the whole warm land far below.', 'snow-crowned, and watching down silently over the whole warm land far below.'),
    (2,11): ('From its slopes, a single river runs the length of scripture -', 'From its white slopes, a single river runs the length of scripture -'),
    (2,12): ('and here, the text says, the corruption first entered the world.', 'and here, the old text says, the corruption first entered the world.'),
    (2,13): ('They came down and took human wives, the account says -', 'They came down and took human wives for themselves, the account says -'),
    (2,14): ('and taught them things that were never meant for the earth.', 'and taught them dark things that were never meant for the earth.'),
    (2,15): ('Metal and blade and forge-fire, the old book plainly says -', 'The working of metal and blade and fire, the old book says -'),
    (2,16): ('and secrets the sky above was never supposed to give them.', 'and bright secrets the sky above was never supposed to give them.'),
    (2,17): ('And from those forbidden unions, the first giants were born -', 'And from those forbidden unions, the first towering giants were finally born -'),
    (2,18): ('the mighty men of renown, the old account calls them.', 'the mighty men of renown, as the old account itself calls them.'),
    (2,19): ('They grew beyond anything the whole earth could ever feed -', 'They grew far beyond anything the whole earth could ever hope to feed -'),
    (2,21): ('And so the whole world tilted down into open violence -', 'And so the whole wide world tilted down into open, endless violence -'),
    (2,23): ('And the ruin, the book insists, did not stay on land -', 'And the ruin, the old book insists, did not stay on land -'),
    (2,24): ('it reached the beasts, the birds, and the deep sea itself.', 'it reached the beasts, the birds, and even the deep sea itself.'),
    (2,25): ('Now hold on to the question the account never once answers -', 'Now hold on tight to the question the old account never answers -'),
    (2,26): ('the giants were all sons - the mighty men of renown.', 'the giants were all of them sons - the mighty men of renown.'),
    (2,27): ('But if the sons were born, then daughters were born too -', 'But if the sons were born, then surely daughters were born too -'),
    (2,28): ('and yet the old texts spend almost no words on them.', 'and yet the old texts spend almost no words at all on them.'),
    (2,29): ('Genesis names only the warriors, the mighty and the powerful -', 'Genesis names only the warriors here, the mighty and the powerful ones -'),
    (2,30): ('and it lets the daughters slip quietly out of the story.', 'and it simply lets the daughters slip quietly out of the story.'),
    (2,31): ('So what became of them - the daughters lost to the water?', 'So what, then, became of them - the daughters lost to the water?'),
    (2,32): ('If the sons among them became the giants of the land -', 'If the sons among them became the towering giants of the land -'),
    (2,33): ('what, then, did the daughters become down in the water?', 'what, then, did the lost daughters become down in the dark water?'),
    (2,34): ('Hold on to that thread - it runs the whole world through.', 'Hold on to that one thread - it runs the whole world through.'),
    (2,35): ('Because the flood, when at last it came, judged the land -', 'Because the great flood, when at last it came, judged the land -'),
    (2,37): ('But water does not drown what already lives within the water -', 'But water does not ever drown what already lives within the water -'),
    (2,38): ('the sea was never threatened - the sea was its own home.', 'the deep sea was never threatened - the sea was its own home.'),
    (2,39): ('And every ocean on the earth remembers something of her -', 'And every ocean on the whole earth still remembers something of her -'),
    (2,40): ('the same single woman, remembered in a hundred different tongues.', 'one same single woman, remembered in a full hundred different human tongues.'),
    (3,1): ('Every ocean on the whole earth remembers the very same woman -', 'Every ocean on the whole wide earth remembers the very same woman -'),
    (3,2): ('and no one alive can agree on how that ever happened.', 'and no one alive can quite agree on how that ever happened.'),
    (3,3): ('Distant peoples who never met, over oceans they could not cross -', 'Distant peoples who never once met, over oceans they could not cross -'),
    (3,4): ('each drew the very same figure rising out of the water.', 'each drew the very same figure rising up out of the water.'),
    (3,5): ('To know what she is, go back before the flood -', 'To know what she really is, go back to before the flood -'),
    (3,6): ('to the ruin the old book says had spread everywhere.', 'back to the ruin the old book says had by then spread everywhere.'),
    (3,7): ('The corruption, Enoch says, did not stay in the bloodline -', 'The corruption, the book of Enoch says, did not stay in the bloodline -'),
    (3,8): ('it reached the beasts, the birds, the things that creep -', 'it reached the beasts, the birds, and the very things that creep -'),
    (3,9): ('and the account adds three short words most retellings skip -', 'and the old account adds three short words most retellings quietly skip -'),
    (3,10): ('the things, the account says, that swim in the black water.', 'the things, the old account says, that swim in the black water.'),
    (3,11): ('Then the flood came at last, just as the book says -', 'Then the great flood came at last, just as the book says -'),
    (3,12): ('and swept the whole land clean of all that walked it.', 'and swept the whole dark land clean of all that walked it.'),
    (3,13): ('But a flood judges the land - it never judges the deep -', 'But a flood only judges the land - it never judges the deep -'),
    (3,14): ('the sea does not drown what already lives in it.', 'and the deep sea does not drown what already lives in it.'),
    (3,15): ('So the old book leaves a gap it never closes -', 'So the old book itself leaves a gap it never once closes -'),
    (3,16): ('a corruption in the water, and a judgment that missed it.', 'a corruption left in the water, and a judgment that missed it.'),
    (3,17): ('And in that open gap, the lost daughters at last return -', 'And in that one open gap, the lost daughters at last return -'),
    (3,18): ('the very ones the old account had let slip quietly away.', 'the very ones the old account itself had let slip quietly away.'),
    (3,19): ('Because the sons of the Watchers became giants of the land -', 'Because the sons of the Watchers became the giants of the land -'),
    (3,20): ('and something, the old legends say, rose up in the water.', 'and something, the old legends say, rose up out of the water.'),
    (3,21): ('Begin with the very oldest of them all - the Greek sirens -', 'Begin with the very oldest of them all - the ancient Greek sirens -'),
    (3,22): ('and throw out entirely the picture that the movies gave you.', 'and throw out entirely the false picture that the movies gave you.'),
    (3,23): ('The earliest sirens of all had no fish tail at all -', 'The very earliest sirens of all had no fish tail at all -'),
    (3,24): ('they were women with the wings and talons of a bird.', 'they were women with the wide wings and talons of a bird.'),
    (3,25): ('One thing alone never changed across the long thousand years -', 'One thing alone never changed at all across a full thousand years -'),
    (3,26): ('not the shape of her at all, but always the voice.', 'not the shape of her at all - but always, always the voice.'),
    (3,27): ('Homer himself wrote it plainly - the song was a weapon -', 'Homer himself wrote of it plainly - the song itself was a weapon -'),
    (3,28): ('and every last sailor who heard it lost all his will.', 'and every last sailor who heard it lost all of his will.'),
    (3,29): ('They steered straight for the music until the hull broke apart -', 'They steered straight on for the music until the hull broke apart -'),
    (3,30): ('a fatal beauty that ended down in the water, every time.', 'a fatal beauty that always ended down in the water, every time.'),
    (3,31): ('Then cross the entire world to the coast of West Africa -', 'Then cross the entire wide world to the coast of West Africa -'),
    (3,32): ('where she is called Mami Wata - the very mother of water.', 'where she is called Mami Wata - which means the mother of water.'),
    (3,33): ('Beautiful, the old traditions say - and yet never once safe -', 'Beautiful, the old traditions all say - yet she is never once safe -'),
    (3,34): ('she draws men down into a world not their own.', 'and she draws men down into a dark world not their own.'),
    (3,35): ('And her cult, even now, is truly no small thing -', 'And her worship, even now, is truly no small thing at all -'),
    (3,36): ('it runs across a whole continent, and even crossed the sea.', 'it runs across a whole vast continent, and even crossed the sea.'),
    (3,37): ('Two separate peoples, two far oceans, one impossible woman between them -', 'Two separate peoples, two far distant oceans, one impossible woman between them -'),
    (3,38): ('and the pattern, as we will see, has only just begun.', 'and the strange pattern, as we will see, has only just begun.'),
    (3,39): ('How does the whole wide world keep the very same memory?', 'How does the whole wide world hold onto the very same memory?'),
    (3,40): ('The answer, it turns out, runs straight back to that mountain.', 'The answer, it turns out, runs straight back to that cold mountain.'),
    (4,1): ('She is not only Greek, and not only African at all -', 'She is not only Greek, and she is not only African at all -'),
    (4,2): ('the exact same figure waits on almost every map we have.', 'the exact same figure waits on almost every ancient map we have.'),
    (4,3): ('Go now to Mesopotamia - the ancient cradle of the world itself -', 'Go now to ancient Mesopotamia - the very cradle of the world itself -'),
    (4,4): ('the very ground where the book of Genesis begins its story.', 'the very ground where the book of Genesis first begins its story.'),
    (4,5): ('The Babylonians carved her image deep into their ancient walls -', 'The old Babylonians carved her image deep into their ancient temple walls -'),
    (4,6): ('half a woman and half a fish, from before the flood.', 'half a woman and half a fish, from long before the flood.'),
    (4,7): ('A being they called Oannes rose up out of the sea -', 'A being that they called Oannes rose up out of the sea -'),
    (4,8): ('and taught all mankind knowledge it was never meant to have.', 'and taught all of mankind knowledge it was never meant to have.'),
    (4,9): ('And the echo here is simply impossible to miss at all -', 'And the echo of it is simply impossible to miss at all -'),
    (4,10): ('for Enoch says the Watchers taught humankind the very same things.', 'for the book of Enoch says the Watchers taught humankind the same.'),
    (4,11): ('The very oldest mermaid of them all was, in fact, Syrian -', 'The very oldest mermaid of them all was, in plain fact, Syrian -'),
    (4,12): ('a full goddess carved in stone and given real worship there.', 'a full goddess carved in ancient stone and given real worship there.'),
    (4,13): ('This is not the edge of the map inventing a tale -', 'This is not the far edge of the map inventing a tale -'),
    (4,14): ('it is the very heart and center of the biblical world.', 'it is the very heart and center of the whole biblical world.'),
    (4,15): ('And past all reason at all, the pattern just keeps spreading -', 'And past all reason at all, the strange pattern just keeps spreading -'),
    (4,16): ('out to far peoples who had never heard the name Homer.', 'out to far distant peoples who had never heard the name Homer.'),
    (4,17): ('Far in the Amazon, they know her as the Iara -', 'Far in the deep Amazon, they know her only as the Iara -'),
    (4,18): ('the mother of the water, whose song draws men down.', 'the mother of all the water, whose song draws helpless men down.'),
    (4,19): ('In the cold Slavic rivers, they know her as the Rusalka -', 'In the cold Slavic rivers, they know her only as the Rusalka -'),
    (4,20): ('a woman of deadly, luring beauty, waiting there in the water.', 'a woman of deadly, luring beauty, waiting silently there beneath the water.'),
    (4,21): ('In far Japan, they tell of the Ningyo - a fish-woman -', 'And in far Japan, they too tell of the Ningyo - a fish-woman -'),
    (4,22): ('and first written of there, in Japan, a thousand years ago.', 'and first written of there, in old Japan, a thousand years ago.'),
    (4,23): ('On the cold, wet coasts of Ireland, there is the Selkie -', 'And on the cold, wet coasts of Ireland, there is the Selkie -'),
    (4,24): ('who sheds her grey sealskin and walks ashore as a woman.', 'who sheds her grey sealskin and walks up ashore as a woman.'),
    (4,25): ('But she is always drawn back again to the sea -', 'But she is always drawn back again, in the end, to the sea -'),
    (4,26): ('and always, in the end, leaving the land behind her.', 'and always, in the very end, leaving the dry land behind her.'),
    (4,27): ('On every continent, in every ocean, in every single age -', 'On every far continent, in every ocean, in every single passing age -'),
    (4,28): ('and all arriving, in the end, at the very same woman.', 'and all arriving, in the very end, at the very same woman.'),
    (4,30): ('tied always to the deep water - and always the voice.', 'and tied always to the deep, dark water - and always the voice.'),
    (4,31): ('Two lone witnesses agreeing on it is only a coincidence -', 'Now two lone witnesses agreeing on it is only a passing coincidence -'),
    (4,32): ('but a full hundred of them agreeing is something else entirely.', 'but a full hundred of them all agreeing is something else entirely.'),
    (4,33): ('These peoples never traded, and they had never once met -', 'These far peoples never traded with each other, and never once met -'),
    (4,34): ('yet each drew the same creature down to the smallest details.', 'yet each one drew the same creature down to the smallest details.'),
    (4,35): ('A myth always drifts - it shifts a little with every telling -', 'A myth always drifts and shifts a little with every single telling -'),
    (4,36): ('but this single one barely moves at all across the world.', 'but this single one barely moves at all across the whole world.'),
    (4,37): ('That, some who study this closely say, is the line -', 'That, some who study this closely say, is precisely the dividing line -'),
    (4,38): ('the fine line between a mere myth and a real memory.', 'the fine line drawn between a mere myth and a real memory.'),
    (4,39): ('And a real memory, they say, holds fast to its shape -', 'And a real memory, they say, always holds fast to its shape -'),
    (4,40): ('because it is remembering something that had really once been real.', 'because it is truly remembering something that had really once been real.'),
    (5,1): ('Before we go any further, the skeptic deserves his say -', 'Now, before we go any further, the skeptic deserves his full say -'),
    (5,2): ('and not the lazy version - the strongest one there is.', 'and not the lazy version of it - the strongest one there is.'),
    (5,3): ('The easy answer is that people simply share the same fears -', 'The easy answer is that all people simply share the same fears -'),
    (5,4): ('water is deeply dangerous, and beauty is always distracting to men.', 'water is deeply dangerous, and beauty is always deeply distracting to men.'),
    (5,5): ('Put those two simple fears together, and the argument runs on -', 'Put those two simple human fears together, and the argument runs on -'),
    (5,7): ('It is a serious answer - and it explains the frame -', 'Now it is a serious answer - and it does explain the frame -'),
    (5,10): ('it cannot explain the same woman, down to the details.', 'but it cannot explain the same woman, down to the finest details.'),
    (5,11): ('The voice as a weapon - not just a pretty sound -', 'The voice used as a weapon - and not just a pretty sound -'),
    (5,12): ('the pull that overrides a man, instead of tempting him.', 'the strange pull that overrides a man, instead of merely tempting him.'),
    (5,14): ('and a fate that is fatal, every single time, without fail.', 'and a fate that proves fatal, every single time, without any fail.'),
    (5,15): ("Then comes the very deepest version of the skeptic's case -", "And then comes the very deepest version of the skeptic's whole case -"),
    (5,16): ('and it needs no watchers and no giants at all.', 'and it needs no watchers and no giants of any kind at all.'),
    (5,17): ('The human mind, it says, carries its own inherited shapes -', 'The human mind, it says, carries within it its own inherited shapes -'),
    (5,18): ('deep molds that every one of us is born already holding.', 'deep molds that every single one of us is born already holding.'),
    (5,19): ('On this view she rises from within, not from the sea -', 'On this strange view she rises from within, not from the sea -'),
    (5,20): ('the feminine that draws and threatens, joined to the deep.', 'the feminine that draws and yet threatens, joined to the deep water.'),
    (5,21): ('By that same logic, any people at all would draw her -', 'By that very same logic, any people at all would draw her -'),
    (5,22): ('not because they ever saw her - but because they carry her.', 'not because they ever once saw her - but because they carry her.'),
    (5,23): ('It is an elegant answer, and an honest one too -', 'It is an elegant answer, and it is an honest one too -'),
    (5,24): ('and it would be truly dishonest to just wave it away.', 'and it would be truly dishonest of us to just wave it away.'),
    (5,25): ('But it, too, strains right where the detail is sharpest -', 'But this one, too, strains right where the fine detail is sharpest -'),
    (5,26): ('the voice, the deep water, the fate that never varies.', 'the voice, the deep dark water, and the fate that never varies.'),
    (5,27): ('The archetype explains the wide frame that is drawn around her -', 'The archetype explains the wide broad frame that is drawn around her -'),
    (5,28): ('but not the fine precision of the picture inside it.', 'but it cannot explain the fine precision of the picture inside it.'),
    (5,29): ('We will not pretend that either side has been fully proven -', 'We will not here pretend that either side has been fully proven -'),
    (5,30): ('only watch where each is strong, and where each strains.', 'only to watch where each is strong, and where each one strains.'),
    (5,31): ('And if it is a memory - a memory of what?', 'And if it truly is a memory - then a memory of what?'),
    (5,32): ('and the question runs straight back to before the flood itself.', 'and so the question runs straight back to before the flood itself.'),
    (5,33): ('To the one old book that treats her as real -', 'Back to the one old book that treats her as fully real -'),
    (5,34): ('not as poetry at all, but as something that truly happened.', 'not as mere poetry at all, but as something that truly happened.'),
    (5,35): ('And the answer, it turns out, is hidden in the words -', 'And the answer, it turns out, lies hidden within the very words -'),
    (5,36): ('in a handful the old translators could not agree on.', 'in a small handful the old translators could never once agree on.'),
    (5,37): ('One word the ancients reached for meant a hybrid thing -', 'One old word the ancients reached for meant a strange hybrid thing -'),
    (5,38): ('a strange being that was never quite fully of this world.', 'a strange being that was never at all fully of this world.'),
    (5,39): ('And it appears where the land lies cursed and empty -', 'And it appears only where the land lies cursed and emptied out -'),
    (5,40): ('where only the things that are not fully human still remain.', 'the place where only things that are not fully human still remain.'),
    (6,2): ('in a handful the old translators could never pin down.', 'in a small handful the old translators could never once pin down.'),
    (6,3): ('One of them appears in the prophet Isaiah - the word lilit -', 'One of them appears in the book of Isaiah - the word lilit -'),
    (6,4): ('and from that single word the translations scatter in every direction.', 'and from that one single word the translations scatter in every direction.'),
    (6,5): ('Some render it as owl, and some as a night creature -', 'Some render it as an owl, and some as a night creature -'),
    (6,6): ('while others just gave up and left it wholly untranslated there.', 'while still others just gave up and left it wholly untranslated there.'),
    (6,7): ('But the very oldest Greek version chose a different word -', 'But the very oldest Greek version of all chose a different word -'),
    (6,8): ('it called her a hybrid - half one thing, half another.', 'it called her a strange hybrid thing - half one thing, half another.'),
    (6,9): ('And read closely just where the prophet actually sets her down -', 'And read very closely just where the prophet actually sets her down -'),
    (6,10): ('in a cursed and emptied land, long after the judgment.', 'in some cursed and emptied out land, long after the great judgment.'),
    (6,11): ('Where only the things not fully human are left to remain -', 'The place where only things not fully human are left to remain -'),
    (6,12): ('that, the old text plainly says, is where she now dwells.', 'that, the old text plainly says, is exactly where she now dwells.'),
    (6,13): ('And around that single word, a whole figure slowly grew up -', 'And around that one single word, a whole figure slowly grew up -'),
    (6,14): ('feminine, and supernatural, and tied to the night and the deep.', 'feminine, and supernatural, and forever tied to the night and the deep.'),
    (6,15): ('Then a second word runs through the old text - tannin -', 'Then a second strange word runs on through the old text - tannin -'),
    (6,16): ('translated dragon in one place, sea monster in the next.', 'translated as dragon in one place, sea monster in the very next.'),
    (6,17): ('And here, at long last, is where the point turns sharp -', 'And here, at very long last, is where the point turns sharp -'),
    (6,18): ('the flood judged the land, but the sea stayed beyond it.', 'the great flood judged the land, but the sea stayed beyond it.'),
    (6,20): ('the place where God himself describes the great and vast Leviathan.', 'the very place where God himself describes the great and vast Leviathan.'),
    (6,21): ('A creature of the deep that no weapon can wound -', 'A vast creature of the deep that no weapon can ever wound -'),
    (6,22): ('that breathes out fire, and dwells where all light gives out.', 'one that breathes out fire, and dwells where all light gives out.'),
    (6,23): ('And the most striking thing is who speaks of it -', 'And the most striking thing of all is who speaks of it -'),
    (6,24): ('not a poet, but God, as a real and present thing.', 'not some poet, but God himself, as a real and present thing.'),
    (6,25): ('For the ancient writer, the sea was never just water -', 'For the ancient writer, the wide sea was never just plain water -'),
    (6,26): ('it was the deep - the place order never fully reached.', 'it was the deep - the very place order never fully reached below.'),
    (6,27): ('The book of Genesis says it in its very second breath -', 'The book of Genesis itself says it in its very second breath -'),
    (6,28): ('darkness over the face of the deep, before all else.', 'darkness over the face of the deep water, before all else came.'),
    (6,29): ('And other lines name a monster the sea still holds -', 'And still other lines name a monster the sea yet still holds -'),
    (6,30): ('a chaos the divine hand had to press back down.', 'a raw chaos the divine hand once had to press back down.'),
    (6,31): ('The old world knew what lived in the deep places -', 'The old world clearly knew what lived down in the deep places -'),
    (6,32): ('a deep knowledge that we ourselves have since lost almost entirely.', 'a deep knowledge that we ourselves have since lost almost completely now.'),
    (6,33): ('And they wrote all of it down, not as mere legend -', 'And they wrote every bit of it down, not as mere legend -'),
    (6,34): ('but as sober fact, in the very plainest words they had.', 'but as sober plain fact, in the very plainest words they had.'),
    (6,35): ('So the very words themselves keep pointing us all one way -', 'So the very words themselves keep pointing us all in one direction -'),
    (6,36): ('back to the deep, and to what the flood never touched.', 'back to the deep, and back to what the flood never touched.'),
    (6,37): ('A corruption that had reached down, at last, into the water -', 'A deep corruption that had reached down, at last, into the water -'),
    (6,38): ('and a judgment that fell only upon the dry land.', 'and a judgment that fell, in the end, only upon the land.'),
    (6,39): ('Two facts, the old book leaves standing side by side -', 'Two plain facts, the old book leaves standing there side by side -'),
    (7,1): ('Now, at last, set the whole thing carefully in order -', 'Now, at long last, set the whole thing down carefully into order -'),
    (7,2): ('because it is when the picture lines up that it holds.', 'because it is only when the picture lines up that it holds.'),
    (7,3): ('The Watchers first came down, all drawn down by human women -', 'The Watchers first came down, all of them drawn by human women -'),
    (7,4): ('and from them the giants were born, the men of renown.', 'and from them the great giants were born, the men of renown.'),
    (7,5): ('But now watch the strange shape of it - the symmetry itself -', 'But now watch closely the strange shape of it - the symmetry itself -'),
    (7,7): ('The great fathers came down, down through the human women below -', 'The great fathers first came down, down through the human women below -'),
    (7,8): ('a descent - down out of the sky, into the world.', 'a descent - down out of the high sky, into the world below.'),
    (7,9): ('And the reflection, the legends say, rose the other way -', 'And the reflection of it, the legends say, rose the other way -'),
    (7,10): ('up through the men - an ascent, out of the water.', 'up through the men - an ascent, up out of the deep water.'),
    (7,11): ('The daughters carried within them the same nature as the sons -', 'The daughters carried within them the very same nature as the sons -'),
    (7,13): ('The one of them came down, down through the open sky -', 'The one of them came down, down through the wide open sky -'),
    (7,14): ('and the other one rose up, up through the deep sea.', 'and the other one rose up, up through the deep dark sea.'),
    (7,15): ('The old book, remember, says the Bible does not close it -', 'The old book, remember, says the Bible itself does not close it -'),
    (7,16): ('it names no verse that follows her into the deep.', 'it names no single verse that follows her down into the deep.'),
    (7,17): ('What it gives us instead is a far stranger fact indeed -', 'What it gives us instead is a far stranger fact than that -'),
    (7,18): ('the flood was meant to end them - and did not.', 'the great flood was meant to end them - and yet did not.'),
    (7,19): ('Because the giants themselves come back, even after the water -', 'Because the giants themselves come right back, even after the great water -'),
    (7,20): ('whole peoples of them, each with their own names and lands.', 'whole peoples of them, each one with their own names and lands.'),
    (7,21): ('The spies that Moses sent came back utterly terrified of them -', 'The spies that Moses sent out came back utterly terrified of them -'),
    (7,22): ('we were as mere grasshoppers, they said, standing before them.', 'we were like mere grasshoppers, they said, when standing there before them.'),
    (7,23): ('And the plainest case the text records is a king -', 'And the plainest single case the text records is that of a king -'),
    (7,24): ('Og of Bashan - the very last of a giant line.', 'It was Og of Bashan - the very last of a giant line.'),
    (7,26): ('it carefully records the sheer size of his great iron bed.', 'it carefully records the sheer size of his great black iron bed.'),
    (7,27): ('It stretched more than four whole meters in length, that bed -', 'It stretched more than four whole meters in length, that iron bed -'),
    (7,28): ('as if a scribe wanted to prove it was no tale.', 'as if some scribe had wanted to prove it was no tale.'),
    (7,29): ('And this was a full thousand years after the great flood -', 'And this was fully a thousand years after the great flood itself -'),
    (7,30): ('long after the water should surely have erased them all.', 'long after the flood water should, by rights, have erased them all.'),
    (7,31): ('Somehow, that which should have vanished had come back once more -', 'And somehow, that which should have vanished had come back once more -'),
    (7,32): ('not as a legend, but as flesh, bone, and iron.', 'and not as a legend, but as real flesh, bone, and iron.'),
    (7,34): ('it simply records the plain fact, and then moves quietly on.', 'it simply records the plain hard fact, and then moves quietly on.'),
    (7,35): ('Leaving the plain contradiction sitting right there upon the page -', 'Leaving the whole plain contradiction just sitting right there upon the page -'),
    (7,36): ('for anyone at all who has the eyes to notice it.', 'for anyone at all who still has the eyes to notice it.'),
    (7,37): ('If the sons somehow survived the water on the land -', 'If the sons of them somehow survived the water on the land -'),
    (7,38): ('then what survived it all, the legends ask, in the sea?', 'then what survived it all, the old legends ask, in the sea?'),
    (7,39): ('And now, at last, the story is very nearly whole -', 'And now, at last, the story is very nearly whole and complete -'),
    (7,40): ('and it ends, of all places, out at the sea.', 'and it ends, of all the places, out at the open sea.'),
    (8,1): ('The story is nearly whole - and it ends at the sea.', 'The whole story is nearly complete - and it ends at the sea.'),
    (8,2): ('Turn now to the very last book of the whole Bible.', 'Turn now, then, to the very last book of the whole Bible.'),
    (8,3): ('John writes of a new heaven and a new earth -', 'John writes of a whole new heaven and a whole new earth -'),
    (8,4): ('and the first heaven and the first earth had passed away.', 'and the first old heaven and the first earth had passed away.'),
    (8,5): ('And then he adds four words almost no one pauses on -', 'And then he adds four small words almost no one pauses on -'),
    (8,6): ('and then he says it plainly - the sea was no more.', 'and then he says it quite plainly - the sea was no more.'),
    (8,7): ('Of every single thing he could have named as finally gone -', 'Of every single thing that he could have named as finally gone -'),
    (8,8): ('no more death, no more pain, and no more tears -', 'no more death at all, no more pain, and no more tears -'),
    (8,9): ('he makes a point of saying the sea is gone.', 'he makes a real point of saying that the sea is gone.'),
    (8,10): ('Why the sea? Why would that stand among the great promises?', 'But why the sea? Why would that stand among the great promises?'),
    (8,11): ('Because in the old texts the sea was never only water -', 'Because in the old texts the sea itself was never only water -'),
    (8,12): ('it was the deep, the abyss, the place order never reached.', 'it was the deep, the abyss - the place order never once reached.'),
    (8,13): ('John himself writes it from exile, alone on a far island -', 'John himself writes it from his exile, alone on a far island -'),
    (8,15): ('If the sea holds the memory of what came before -', 'If the sea itself holds the memory of what came long before -'),
    (8,16): ('then its ending is not weather, and not mere geography.', 'then its ending is not weather at all, and not mere geography.'),
    (8,17): ('It is a door, the old readers say, finally closing -', 'It is a door, the old readers say, at last finally closing -'),
    (8,18): ('a door that stood open since the days of Noah.', 'a great door that had stood open since the days of Noah.'),
    (8,19): ('Since the Watchers came, and since the giants themselves came -', 'Since the day the Watchers came, and since the giants themselves came -'),
    (8,20): ('and since the daughters who all went down into the water.', 'and since the daughters, too, who all went down into the water.'),
    (8,21): ('Since the sirens who sang up on their bright sea-cliffs -', 'Ever since the sirens who sang out on their bright, windy sea-cliffs -'),
    (8,22): ('since Mami Wata, the mother of the West African rivers -', 'since Mami Wata, who is mother of all the West African rivers -'),
    (8,23): ('since Atargatis, the goddess carved long ago in Syrian stone -', 'since Atargatis, the old goddess carved long ago in pale Syrian stone -'),
    (8,24): ('since Oannes, who rose from the sea to teach the Babylonians -', 'since Oannes, who rose up from the sea to teach the Babylonians -'),
    (8,25): ('since the Iara, singing far out upon the great Amazon river -', 'since the Iara, still singing far out upon the great Amazon river -'),
    (8,26): ('since the pale Rusalka, and since the far-off Ningyo too -', 'since the pale Rusalka, and even since the far-off Japanese Ningyo too -'),
    (8,27): ('since the Selkie out upon the cold and bright northern coasts -', 'since the Selkie out upon the cold and bright northern Irish coasts -'),
    (8,28): ('the water spirits, all of them, of a hundred scattered cultures.', 'the water spirits, every one of them, of a hundred scattered cultures.'),
    (8,29): ('A whole hundred peoples who had never once known one another -', 'A whole hundred peoples who had never even once known one another -'),
    (8,30): ('and who all, somehow, remembered the very same single woman.', 'and yet who all, somehow, still remembered the very same single woman.'),
    (8,31): ('She is always feminine, and yet far more than merely human -', 'She is always feminine, and yet always far more than merely human -'),
    (8,32): ('tied always to the deep water - and always the voice.', 'and tied always to the deep water - and always, always the voice.'),
    (8,33): ('We do not ask you here to close the question -', 'We do not ask you here to close off the question at all -'),
    (8,34): ('only to feel the weight of what gathers, page by page.', 'only to feel the sheer weight of what gathers, page by page.'),
    (8,36): ('because an absent verse is not the same as absent evidence.', 'because an absent verse is never the same as truly absent evidence.'),
    (8,37): ('And what gathers, culture after culture, is hard to set down -', 'And what gathers here, culture after culture, is hard to set down -'),
    (8,38): ('always the same woman, the same water, the same haunting call.', 'it is always the same woman, the same water, the same call.'),
    (8,39): ('The sea, John says, will one day be no more -', 'The sea, John promises, will one day be no more at all -'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="master.csv", help="path to master.csv")
    args = ap.parse_args()
    path = args.csv
    if not os.path.isfile(path):
        sys.stderr.write("ERROR: not found: %s\n" % path); sys.exit(1)

    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        fields = rd.fieldnames
        rows = list(rd)
    for col in ("block_id", "clip_index", "narration"):
        if col not in fields:
            sys.stderr.write("ERROR: master.csv missing column %s\n" % col); sys.exit(1)

    seen = set(); applied = skipped = 0; mismatches = []
    for r in rows:
        try:
            key = (int(r["block_id"]), int(r["clip_index"]))
        except (ValueError, KeyError):
            continue
        if key not in EDITS:
            continue
        seen.add(key)
        old, new = EDITS[key]
        cur = r["narration"]
        if cur == new:
            skipped += 1
        elif cur == old:
            r["narration"] = new; applied += 1
        else:
            mismatches.append((key, cur))

    missing = sorted(set(EDITS) - seen)
    if missing:
        sys.stderr.write("ERROR: %d edit keys not in master: %s\n"
                         % (len(missing), ", ".join("%d/%d" % k for k in missing[:10])))
        sys.exit(1)
    if mismatches:
        sys.stderr.write("ERROR: %d anchor mismatches -- ABORT (no write). Source drifted.\n" % len(mismatches))
        for k, cur in mismatches[:5]:
            sys.stderr.write("  %d/%d current: %r\n" % (k[0], k[1], cur[:70]))
        sys.exit(1)

    if applied == 0:
        print("no changes (all %d beats already at pass-2 lines)" % skipped); return

    bak = path + ".pre_p2enrich"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8") as b, open(path, encoding="utf-8") as o:
            b.write(o.read())
        print("backup:", bak)

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print("OK: pass-2 enrichment applied. beats changed: %d | already-done: %d" % (applied, skipped))


if __name__ == "__main__":
    main()
