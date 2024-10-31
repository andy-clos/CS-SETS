Master Branch

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

Git commands:

| Command                           | Action                                                                                 |
| :-------------------------------- | :------------------------------------------------------------------------------------- |
| `git pull origin dev`             | Get the latest code from everyone                                                      |
| `git commit -m "commit messages"` | To commit the change that you have done (it does not push into GitHub server yet)      |
| `git push origin dev`             | To push the code that you committed above into GitHub server                           |


NPM Commands:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`      |
| `npm run build`           | Build your production site to `./dist/`          |
| `npm run preview`         | Preview your build locally, before deploying     |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |
