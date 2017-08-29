# =============================================================================
# Message and dialog handler in xtgeo. It works together the logging module,
# But, also I need stuff to work together with existing
# Perl and C libraries...
#
# How it should works:
# Enviroment variable XTG_VERBOSE_LEVEL will steer the output from lowelevel
# C routines; normally they are quiet
# XTG_VERBOSE_LEVEL is undefined: xtg.say works to screen
# XTG_VERBOSE_LEVEL > 1 starts to print C messages
# XTG_VERBOSE_LEVEL < 0 skip also xtg.say
#
# XTG_LOGGING_LEVEL is for Python logging (string, as INFO)
# XTG_LOGGING_FORMAT is for Python logging (number, 0 ,1, 2, ...)
#
# The system here is:
# syslevel is the actual level when code is executed:
#
# -1: quiet dialog, no warnings only errors and critical
# 0 : quiet dialog, only warnings and errors will be displayed
# JRIV
# =============================================================================


import os
import sys
import inspect
import logging
import xtgeo
import cxtgeo

class XTGeoDialog(object):
    """
    System for handling dialogs and messages in XTGeo, which cooperates
    with Python logging module.

    """

    def __init__(self):
        """
        The __init__ (constructor) method.

        Args: none so far
        """

        # a number, for C routines
        envsyslevel = os.environ.get('XTG_VERBOSE_LEVEL')

        # a string, for Python logging:
        logginglevel = os.environ.get('XTG_LOGGING_LEVEL')

        # a number, for format, 1 is simple, 2 is more info etc
        loggingformat = os.environ.get('XTG_LOGGING_FORMAT')

        if envsyslevel is None:
            self._syslevel = 0
        else:
            self._syslevel = int(envsyslevel)

        if logginglevel is None:
            self._logginglevel = 'CRITICAL'
        else:
            self._logginglevel = str(logginglevel)

        if loggingformat is None:
            self._lformatlevel = 1
        else:
            self._lformatlevel = int(loggingformat)

    @property
    def syslevel(self):
        return self._syslevel

    # for backward compatibility (to be phased out)
    def get_syslevel(self):
        return self._syslevel

    @property
    def logginglevel(self):
        """Will return a logging level property, e.g. logging.CRITICAL"""
        ll = logging.CRITICAL
        if self._logginglevel == 'INFO':
            ll = logging.INFO
        elif self._logginglevel == 'WARNING':
            ll = logging.WARNING
        elif self._logginglevel == 'DEBUG':
            ll = logging.DEBUG

        return ll

    @property
    def loggingformatlevel(self):
        return self._lformatlevel

    @property
    def loggingformat(self):
        """Returns the format string to be used in logging"""

        if self._lformatlevel <= 1:
            self._lformat = '%(name)44s %(funcName)44s '\
                + '%(levelname)8s: \t%(message)s'
        else:
            self._lformat = '%(msecs)6.2f Line: %(lineno)4d %(name)44s '\
                + '[%(funcName)40s()]'\
                + '%(levelname)8s:'\
                + '\t%(message)s'

        return self._lformat

    @syslevel.setter
    def syslevel(self, mylevel):
        if mylevel >= 0 and mylevel < 5:
            self._syslevel = mylevel
        else:
            print("Invalid range for syslevel")

        envsyslevel = os.environ.get('XTG_VERBOSE_LEVEL')

        if envsyslevel is None:
            pass
        else:
            # print("Logging overridden by XTG_VERBOSE_LEVEL = {}"
            #       .format(envsyslevel))
            self._syslevel = int(envsyslevel)

    @staticmethod
    def print_xtgeo_header(appname, appversion):
        """
        Prints a XTGeo banner for an app to STDOUT.
        """

        cur_version = 'Python ' + str(sys.version_info[0]) + '.'
        cur_version += str(sys.version_info[1]) + '.' \
            + str(sys.version_info[2])

        app = appname + ' (version ' + str(appversion) + ')'
        print('')
        print('#' * 79)
        print('#{}#'.format(app.center(77)))
        print('#' * 79)
        ver = 'XTGeo4Python version ' + xtgeo.__version__
        ver = ver + '(CXTGeo v. ' + cxtgeo.__version__ + ')'
        print('#{}#'.format(ver.center(77)))
        print('#{}#'.format(cur_version.center(77)))
        print('#' * 79)
        print('')

    def insane(self, string):
        level = 4
        idx = 0

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def trace(self, string):
        level = 3
        idx = 0

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def debug(self, string):
        level = 2
        idx = 0

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def speak(self, string):
        level = 1
        idx = 1

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    info = speak

    def say(self, string):
        level = -5
        idx = 3

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def warn(self, string):
        level = 0
        idx = 6

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    warning = warn

    def error(self, string):
        level = -8
        idx = 8

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)

    def critical(self, string):
        level = -9
        idx = 9

        caller = sys._getframe(1).f_code.co_name
        frame = inspect.stack()[1][0]
        self.get_callerinfo(caller, frame)

        self._output(idx, level, string)
        sys.exit(1)

    def get_callerinfo(self, caller, frame):
        the_class = self._get_class_from_frame(frame)

        # just keep the last class element
        x = str(the_class)
        x = x.split('.')
        the_class = x[-1]

        self._caller = caller
        self._callclass = the_class

        return (self._caller, self._callclass)

# =============================================================================
# Private routines
# =============================================================================

    def _get_class_from_frame(self, fr):
        args, _, _, value_dict = inspect.getargvalues(fr)
        # we check the first parameter for the frame function is
        # named 'self'
        if len(args) and args[0] == 'self':
            instance = value_dict.get('self', None)
            if instance:
                # return its class
                return getattr(instance, '__class__', None)
        # return None otherwise
        return None

    def _output(self, idx, level, string):

        if idx == 0:
            prefix = '++'
        elif idx == 1:
            prefix = '**'
        elif idx == 3:
            prefix = '>>'
        elif idx == 6:
            prefix = '##'
        elif idx == 8:
            prefix = '!#'
        elif idx == 9:
            prefix = '!!'

        prompt = False
        if level <= self._syslevel:
            prompt = True

        if prompt:
            if self._syslevel <= 1:
                print('{} {}'.format(prefix, string))
            else:
                ulevel = str(level)
                if (level == -5):
                    ulevel = 'M'
                if (level == -8):
                    ulevel = 'E'
                if (level == -9):
                    ulevel = 'W'
                print('{0} <{1}> [{2:23s}->{3:>33s}] {4}'
                      .format(prefix, ulevel, self._callclass,
                              self._caller, string))


# =============================================================================
# MAIN, for initial testing. Run from current directory
# =============================================================================
def main():

    xtg = XTGeoDialog()

    xtg.speak("Level 1 text")
    xtg.debug("Level 2 text debug should not show")

    xtx = XTGeoDialog()

    # can use both class and instacne her (since this is a classmethod)
    print("Syslevel (instance) is {}".format(xtx.syslevel))

    xtx.speak("Level 1 speak text")
    xtx.info("Level 1 info text")

    mynumber = 2233.2293939
    xtx.say('My number is {0:6.2f}'.format(mynumber))

    xtg.syslevel(2)

    print("Syslevel is " + str(xtg.syslevel))

    xtg.debug("Level 2 (debug) text should show now")
    xtg.say("Say hello ...")

    xtg.error("Errors are always shown as long as level > -9")


if __name__ == '__main__':
    main()