import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

function checkDir(dirPath) {
    if (!fs.existsSync(dirPath)) return;
    
    console.log(`Scanning ${dirPath}...`);
    let errorCount = 0;
    
    function walkSync(currentDirPath) {
        fs.readdirSync(currentDirPath).forEach(function(name) {
            var filePath = path.join(currentDirPath, name);
            var stat = fs.statSync(filePath);
            if (stat.isFile() && filePath.endsWith('.md')) {
                try {
                    const content = fs.readFileSync(filePath, 'utf8');
                    const match = content.match(/^---\n([\s\S]*?)\n---/);
                    if (match) {
                        const yamlStr = match[1];
                        try {
                            const parsed = yaml.load(yamlStr);
                            if (parsed !== undefined && parsed !== null) {
                                if (typeof parsed !== 'object' || Array.isArray(parsed)) {
                                    console.log(`\n[X] CRITICAL DATA TYPE ERROR in ${filePath}: parsed YAML is not an object! (Type: ${typeof parsed}, Array: ${Array.isArray(parsed)})`);
                                    errorCount++;
                                }
                            } else {
                                console.log(`\n[X] CRITICAL DATA TYPE ERROR in ${filePath}: parsed YAML is null/undefined! (Maybe empty frontmatter?)`);
                                errorCount++;
                            }
                        } catch (e) {
                            console.log(`\n[X] CRITICAL YAML ERROR in ${filePath}:`);
                            console.log(e.message);
                            errorCount++;
                        }
                    } else {
                        // console.log(`No frontmatter in ${filePath}`);
                    }
                } catch (e) {
                    console.log(`Could not read ${filePath}: ${e.message}`);
                }
            } else if (stat.isDirectory()) {
                walkSync(filePath);
            }
        });
    }
    
    walkSync(dirPath);
    if (errorCount === 0) {
        console.log(`All logic checks passed in ${dirPath}!`);
    }
}

checkDir('/home/terwu01/github/marffet/.agent/workflows');
checkDir('/home/terwu01/github/marffet/.agent/skills');
