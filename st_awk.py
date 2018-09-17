# -*- coding: utf-8 -*-
import sublime, sublime_plugin
from subprocess import Popen, PIPE, STDOUT

class awk_runCommand(sublime_plugin.TextCommand):
    def run_(self, edit_token, args):
        """
        Actually run awk command
        """
        expr, inplace = args.get('expr'), args.get('inplace')

        if expr == None:
            return

        r = sublime.Region(0, self.view.size())
        content = self.view.substr(r)

        try:
            p = Popen(['awk', expr], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            out, err = map(bytes.decode, p.communicate(input=content.encode('utf8')))
            if err:
                sublime.error_message('Error when run awk: \n' + err)
                return
        except OSError as e:
            sublime.error_message('''Error when run command awk: %s, errno: %d.\nawk is required on $PATH''' 
                % (e.strerror, e.errno))
            return
        except Exception as e:
            sublime.error_message('''Error when run command awk: %s''' % e)
            return

        if inplace:
            edit = self.view.begin_edit(edit_token, self.name())
            self.view.replace(edit, r, out)
            self.view.end_edit(edit)
        else:
            new_view = self.view.window().new_file()
            edit = new_view.begin_edit(edit_token, self.name())
            new_view.insert(edit, 0, out)
            new_view.end_edit(edit)

class st_awkCommand(sublime_plugin.TextCommand):
    def run(self, *args, **kwargs):
        """
        args: 
            'inplace' : if it's 'yes', replace current view with command result 
        """
        inplace = kwargs['inplace'].lower() == 'yes'
        def onDone(expr):
            self.view.run_command('awk_run', {'expr': expr, 'inplace': inplace})

# TODO in-line awk expr or .awk file
        self.view.window().show_input_panel('Awk expression:', '', onDone, None, None)
