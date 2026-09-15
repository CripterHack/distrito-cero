"""Launch configuration shared by current browser tests, not by the game."""
import os

def launch_options(args=None):
    result={'headless':os.environ.get('DC_QA_HEADLESS','1')!='0', 'args':args or ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']}
    if os.environ.get('DC_QA_BROWSER'): result['executable_path']=os.environ['DC_QA_BROWSER']
    return result
