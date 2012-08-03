import re

from forum.models import User,  Question,  Answer,  Comment

def find_best_match_in_name(content,  uname,  fullname,  start_index):      
    end_index = start_index + len(fullname)    
    
    while end_index > start_index:
        if content[start_index : end_index].lower() == fullname.lower():
            return content[start_index : end_index]
            
        while len(fullname) and fullname[-1] != ' ':
            fullname = fullname[:-1]
            
        fullname = fullname.rstrip()
        end_index = start_index + len(fullname)
            
    return uname    

APPEAL_PATTERN = re.compile(r'(?<!\w)@\w+')

def auto_user_link(node, content):
    
    # We should find the root of the node tree (question) the current node belongs to.
    if isinstance(node,  Question):
        question = node
    elif isinstance(node,  Answer):
        question = node.question
    elif isinstance(node,  Comment):
        if node.question:
            question = node.question
        elif node.answer:
            question = node.answer.question
    else:
        return content
    
    # Now we've got the root question. Let's get the list of active users.
    active_users = question.get_active_users()
    
    appeals = APPEAL_PATTERN.finditer(content)

    replacements = []

    for appeal in appeals:
        # Try to find the profile URL
        username = appeal.group(0)[1:]
        
        matches = []
        
        for user in active_users:
            if user.username.lower().startswith(username.lower()):
                matches.append(user)
                
        if len(matches) == 1:
            replacements.append(
                                (find_best_match_in_name(content,  username,  matches[0].username,  appeal.start(0) + 1),  matches[0])
                                )                                
        elif len(matches) == 0:
            matches = User.objects.filter(username__istartswith=username)
            
        if (len(matches) == 0):
                continue
        
        best_user_match = None
        final_match = ""
        
        for user in matches:
            user_match = find_best_match_in_name(content,  username,  user.username,  appeal.start(0) + 1)
            
            if (len(user_match) < len(final_match)): 
                continue
                
            if (len(user_match) == len(final_match)):
                if not (user.username.lower() == user_match.lower()):
                    continue
                    
                if (best_user_match and (best_user_match.username == final_match)):
                    continue
                    
            best_user_match = user
            final_match = user_match
        
        replacements.append((final_match,  best_user_match))            
    
    for replacement in replacements:
        to_replace = "@" + replacement[0]
        profile_url = replacement[1].get_absolute_url()
        
        auto_link = '<a href="%s">%s</a>' % (profile_url, to_replace)
        content = content.replace(to_replace, auto_link)        
    
    return content
