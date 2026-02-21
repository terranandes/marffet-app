with open('app/main.py', 'r') as f:
    text = f.read()

# Fix the broken indents. They all ended up with 8 spaces indent for `pass`
# Let's just fix the 3 patterns directly
text = text.replace("    except Exception:\n        pass\n", "    except Exception:\n        pass\n") # This one actually looks ok, maybe 118
text = text.replace("            except Exception:\n                pass\n", "            except Exception:\n                pass\n")
text = text.replace("                except Exception:\n        pass\n", "                except Exception:\n                    pass\n")
text = text.replace("            except Exception:\n        pass\n", "            except Exception:\n                pass\n")

with open('app/main.py', 'w') as f:
    f.write(text)

