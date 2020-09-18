import re

from collections import OrderedDict
from pathlib import Path


LICENSE = '''<sub>[Digital Research Institute (DRI) Curriculum](http://purl.org/dc/terms/) by [Graduate Center Digital Initiatives](https://gcdi.commons.gc.cuny.edu/) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/). Based on a work at <https://github.com/DHRI-Curriculum>. When sharing this material or derivative works, preserve this paragraph, changing only the title of the derivative work, or provide comparable attribution.</sub>

[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)'''

IMAGES = r'!\[([^\]]*)\]\((.*?)(?=\"|\))(\".*\")?\)'
ALL_IMAGES = re.compile(IMAGES)

def insert_directory_before_images(string='', directory='../images/', replacement_dict={'images/': ''}):
    output = list()
    for data in ALL_IMAGES.findall(string):
        text, url, _ = data
        original_string = f'![{text}]({url})'

        for string, replacement in replacement_dict.items():
            url = url.replace(string, replacement)

        if url.startswith('/'):
            url = url[1:]
        url = directory + url

        replaced_string = f'![{text}]({url})'
        output.append({
            'original_string': original_string,
            'replaced_string': replaced_string
        })
    return output


def insert_get_started_button(url='', center=True):
    _ = ''
    if center: _ += f'<p align="center">'
    _ += f'<a href="{url}">Get Started</a> →'
    if center: _ += f'</p>'
    _ += '\n\n'
    return _


def slugify(text):
    non_url_safe = ['"', '#', '$', '%', '&', '+', ',', '/', ':', ';', '=', '?', '@', '[', '\\', ']', '^', '`', '{', '|', '}', '~', "'"]
    non_url_safe_regex = re.compile(
        r'[{}]'.format(''.join(re.escape(x) for x in non_url_safe)))

    text = non_url_safe_regex.sub('', text).strip()
    text = u'-'.join(re.split(r'\s+', text))
    return text


def split_into_sections(markdown:str, level_granularity=3, keep_levels=False, clear_empty_lines=True) -> dict:
    """
    Splits a markdown file into a dictionary with the headings as keys and the section contents as values, and returns the dictionary.
    Takes two arguments:
      - level_granularity that can be set to 1, 2, or 3, determining the depth of search for children
      - keep_level which maintains the number of octothorps before the header
    """

    if not isinstance(markdown, str):
        raise RuntimeError('Markdown is not string:', markdown)
    if clear_empty_lines:
        lines = [_ for _ in markdown.splitlines() if _] # cleans out any empty lines
    else:
        lines = markdown.splitlines()

    sections = OrderedDict()

    def is_header(line:str, granularity=level_granularity):
        if granularity == 1:
            if line.startswith("# "): return(True)
        elif granularity == 2:
            if line.startswith("# ") or line.startswith("## "): return(True)
        elif granularity == 3:
            if line.startswith("# ") or line.startswith("## ") or line.startswith("### "): return(True)
        return(False)

    in_code = False
    for linenumber, line in enumerate(lines):
        code = line.startswith('```')
        if code == True:
            if in_code == False:
                in_code = True
            elif in_code == True:
                in_code = False

        if is_header(line) and in_code == False:
            header = ''.join([_ for _ in line.split('#') if _]).strip()
            if keep_levels:
                level = line.strip()[:3].count("#")
                header = f"{'#' * level} {header}"

            if header not in sections:
                sections[header] = ''
                skip_ahead = False
                nextline_in_code = False
                for nextline in lines[linenumber + 1:]:
                    nextline_code = nextline.startswith('```')
                    if nextline_code == True:
                        if nextline_in_code == False:
                            nextline_in_code = True
                        elif nextline_in_code == True:
                            nextline_in_code = False
                    if is_header(nextline) and not nextline_in_code: skip_ahead = True
                    if skip_ahead: continue
                    sections[header] += '\n' + nextline
                sections[header] = sections[header].strip()

    return(sections)


def read(filename:str, required=True):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        if required:
            raise FileNotFoundError(f'Required file `{filename}` could not be found in repository. Make sure it exists before you run this script.') from None
        else:
            return None


def check_sections_directory():
    if Path('sections').exists():
        [Path(x).unlink() for x in Path('sections').glob('*')]
    else:
        Path('sections').mkdir(parents=True)

    return True


def get_nav(counter, all_content, separator='&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;', back_to_start='Start'):
    prev_counter = counter-1
    next_counter = counter+1
    try:
        prev_title = all_content[prev_counter].get('title')
    except KeyError:
        prev_title = back_to_start
    try:
        next_title = all_content[next_counter].get('title')
    except KeyError:
        next_title = back_to_start

    if prev_title == back_to_start:
        file_content = f'↻ [{prev_title}]'
        file_content += '(../README.md)'
    else:
        file_content = f'← [{prev_title}]'
        file_content += f'({prev_counter:02d}-{all_content[prev_counter].get("slug")}.md)'

    file_content += separator

    file_content += f'[{next_title}]'
    if next_title == back_to_start:
        file_content += '(../README.md) ↺'
    else:
        file_content += f'({next_counter:02d}-{all_content[next_counter].get("slug")}.md) →'

    return file_content


def write_lessons(all_content):
    for counter, data in all_content.items():

        # Make any corrections to content here
        content = data.get('content')

        for d in insert_directory_before_images(content):
            content = content.replace(d['original_string'], d['replaced_string'])

        file_content = get_nav(counter, all_content) + '\n\n'
        file_content += '---\n\n'
        file_content += f'# {counter}. {data.get("title")}\n\n'
        file_content += content
        file_content += '\n\n'
        file_content += '---\n\n'
        file_content += get_nav(counter, all_content)

        file_path = Path(f'sections/{counter:02d}-{data.get("slug")}.md')
        file_path.write_text(file_content)

    return True


def get_toc(all_content, as_dict=True):
    toc = OrderedDict()
    for counter, data in all_content.items():
        toc[counter] = {
            'path': f'sections/{counter:02d}-{data.get("slug")}.md',
            'title': data.get("title")
        }
    if as_dict: return toc

    toc_text = ''
    for counter, data in toc.items():
        toc_text += f'{counter}. [{data.get("title")}]({data.get("path")})\n'
    toc_text = toc_text.strip()

    return toc_text


def split_lessons(lessons_file='lessons.md'):
    lessons = read(lessons_file)

    all_content = OrderedDict()
    counter = 1

    for lesson_title, lesson_content in split_into_sections(lessons, level_granularity=1, clear_empty_lines=False).items():
        all_content[counter] = {
            'title': lesson_title,
            'slug': slugify(text=lesson_title.lower()),
            'content': lesson_content
        }
        counter += 1

    return all_content


def split_frontmatter(frontmatter_file='frontmatter.md'):
    frontmatter = read(frontmatter_file)
    frontmatter_sections = split_into_sections(frontmatter, level_granularity=2, clear_empty_lines=False)
    return frontmatter_sections


def get_image_or_title(image_file='image.md', workshop_title=''):
    t = read(image_file, required=False)
    if t:
        return t
    else:
        return f'# {workshop_title}'


def write_readme(filename='README.md', contents=''):
    Path(filename).write_text(contents)
    return True

if __name__ == "__main__":
    raise NotImplemented("Coming soon!")