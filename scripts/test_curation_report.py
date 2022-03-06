
import collections
import asyncio, time, os, sys
import Byond, OpenDream, ClopenDream, Shared

from DTT import App
import test_runner

class Main(App):
    async def run(self):
        env = self.env.branch()

        results = collections.defaultdict(list)
        mm_results = collections.defaultdict(list)

        for tenv in test_runner.list_all_tests(env, main.env.attr.tests.dirs.dm_files):
            benv = tenv.branch()
            benv.attr.install.platform = 'byond'
            benv.attr.install.id = 'default'
            test_runner.Curated.load_test( benv )
            exists = test_runner.Report.load_result( benv )
            if not exists:
                continue
            
            oenv = tenv.branch()
            oenv.attr.opendream.sources['default_full'] = env.attr.opendream.sources['default']
            oenv.attr.install.platform = 'opendream'
            oenv.attr.install.id = 'default_full'
            test_runner.Curated.load_test( oenv )
            exists = test_runner.Report.load_result( oenv )
            if not exists:
                continue

            for pr in env.attr.state['github_prs']['data']:
                repo_name = pr["head"]["repo"]["full_name"].replace("/", ".")
                pr_sha = pr["head"]["sha"]
                install_id = f'github.{repo_name}.{pr_sha}'

                penv = tenv.branch()
                penv.attr.install.platform = 'opendream'
                penv.attr.install.id = install_id
                test_runner.Curated.load_test( penv )

                if not os.path.exists(penv.attr.test.base_dir / "compile.returncode.log"):
                    continue
                exists = test_runner.Report.load_result( penv )
                if not exists:
                    continue
                result = test_runner.Report.compare_results(benv, oenv, penv)

                if result in ["breaking", "fixing"]:
                    results[pr["title"]].append( (penv.attr.test.id, result) )

                if result in ["mismatch"]:
                    mm_results[pr["title"]].append( penv.attr.test.id )

        for title, result in results.items():
            print(title)
            print(result)

        for title, result in mm_results.items():
            print(title)
            print(result)

main = Main()
asyncio.run( main.start() )