# Project
This project contains python script tha creates test data for agent and model evaualtion , based from fixed a set of test results. Then metrics such as average, best / worst are calcualted based on scores and it stores the result to a json +csvfile and also on a console sumamry of result and to a txt file too

# Rules to follow
1. Check before all commits to ensure secrets / credentials/ Tokens are never checked in to github or nay repo
2. whem I say commit, you should be able to extract my git hub credentials stored in GITHUB_PAT variable, in zshrc file
3. Test changes, methods, function etc before commiting, even if I forget to call oit out explcitly. Call out and stop commit if tests are not there and if the tests do not pass