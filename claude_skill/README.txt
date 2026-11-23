CupCarbon Coding Skill for Claude
=================================

Two skills teach Claude to write correct CupCarbon node programs:
  - cupcarbon-coding    : Python scripts for IoT nodes (cup_* API,
                          30 functions, MQTT, agentic bridge)
  - cupcarbon-senscript : SenScript (.csc) programs for classical WSN
                          sensor nodes (full command reference, routing,
                          sensing, elections)

Two ways to install it — pick ONE:

1) Claude app / claude.ai (stored in your Claude account)
   - Drag the file  cupcarbon-coding.skill  (and/or cupcarbon-senscript.skill) into any Claude chat and
     click "Save skill"
   - or: Settings -> Capabilities -> Skills -> Upload skill

2) Claude Code (stored locally, nothing uploaded)
   - Copy the folder(s)  cupcarbon-coding/  and  cupcarbon-senscript/  into  ~/.claude/skills/
     (all your projects), or into  <your project>/.claude/skills/
     (that project only)

Then just ask Claude, e.g.:
  "Write a CupCarbon script where the node publishes its id on
   cupcarbon/fire when it is marked, and the responder script that
   drives to the alerting node."
