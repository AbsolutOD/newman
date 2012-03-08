Newman

This is the first post I have written of this kind.  I am introducing a tool I have written at Adkeeper.com to help manage python code.

History

Before I joined Adkeeper.com, I was mainly a ruby developer writing a lot of rails and sinatra apps.  There is an awesome tool written in ruby called Rake.  You can't work with ruby and not use rake.  Rake is a great tool that let's you write ruby code to help manage your project.

It seems like a lot of python projects write a manage.py script to manage their python app.  You could use make or rake, but what if you had a python module that you want?  You couldn't just import it and reuse it.  You would have to make a python script to import it and use it, so you could call it from make or rake.  So, I get why python projects write their own manage.py script.

After a while our manage.py script had a ton of switches.  It was really unruly and I really missed rake.  So, over Thanksgiving weekend I set out to write a python version of rake.  There were 3 goals I had in mind.

1. Make it really easy to execute python code from the command line.
2. Handle command line arguments better than rake.
3. Have great help docs like rake does.

Newman

At the end of the weekend, I'd met all of these goals.  I think newman makes it extremely easy to organize utility code with the ability to call it from the command line.  You can choose which functions you want to expose and which ones you want hide.  You can define arguments that you want the task to be able to accept and give a nice help description for each argument.

Newman looks for a lib.tasks module.  So, first thing you need to do is create a lib dir with a __init__.py file if you don't already have one.  Next is to create the tasks module.  Every module in the tasks module will be opened and searched for functions that are decorated with a @task decorator.

Let's create a pretend project and create some tasks.  First I will create an empty project dir.  I will call mine "math-app".  Change into that dir and run the following commands.

{{{code

$> mkdir -p lib/tasks
$> touch lib/__init__.py
$> touch lib/tasks/__init__.py

}}}

Now let's create our first newman task module.  I am going to create lib/tasks/math.py as my first task module.

{{{code

from newman import task, Argument

@task(())
def hello(args):
    """I just print out hello"""
    print "Hello out there!"


}}}

Just that little bit of code doesn't do much, but when you run newman it sees the file and it can display some help.  Newman needs to be run from the apps root dir.  So, let's do that now.

{{{code

$> newman -h
usage: newman [-h] [-v] {math} ...

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show version and exit

Task Modules:
  Namespaces for the different sub tasks.

  {math}
    math


}}}

You can see that newman has picked up the math task module we wrote.  That tells us that we have a math task module.  Let's dive deeper.  What tasks does the math task module have?  Let's ask newman.

{{{code

$> newman math -h
usage: newman math [-h] {hello} ...

optional arguments:
  -h, --help  show this help message and exit

Tasks under math:
  {hello}     The following are valid task commands
    hello     I just print out hello


}}}

It is important to note that we can use the -h option at every level down to the task itself for help.  This tells us that the math task module just has a single task.  You will notice that the task has the text from the functions docstring display as the task's description.  Now we know we can run the "hello" task, but are there any arguments that we can pass to it?

"Hello Newman…"

{{{code

$> newman math hello -h
usage: newman math hello [-h]

optional arguments:
  -h, --help  show this help message and exit

}}}

Nope, doesn't look like this task takes arguments.  Let's run it.

{{{code

$> newman math hello
Hello out there!

}}}

You can see that newman has executed the function that we decorated.  Let's add one more function that takes an argument.

{{{code

@task((
    Argument("x", int, "First int to add.", required=True),
    Argument("y", int, "Second int to add.", required=True),
))
def add(args):
    """Takes 2 arguments and adds them together."""
    ans = args.x + args.y
    print "{0} + {1} = {2}".format(args.x, args.y, ans)

}}}

Let's see what the help message for this task looks like.

{{{code

$> newman math add -h
usage: newman math add [-h] --x X --y Y

optional arguments:
  -h, --help  show this help message and exit
  --x X       First int to add.
  --y Y       Second int to add.


}}}

We can see that it has 2 arguments that take values.  What happens if I don't pass in any arguments?

{{{code

$> newman math add
usage: newman math add [-h] --x X --y Y
newman math add: error: argument --x is required

}}}

The param "required=True" is what sets the argument as required or optional.  So, let add something.

{{{code

$> newman math add --x 3 --y 3
3 + 3 = 6

}}}

Sweet!  The one last thing I want to show is that it has some argument validation as well.  The second param to the Argument class is what type of objects you are expecting.  So, since we have 'int' there, it will check that an integer is actually being passed in.

{{{code

$ newman math add --x 3 --y a
usage: newman math add [-h] --x X --y Y
newman math add: error: argument --y: invalid int value: 'a'

}}}

That covers the basic features of newman.  You might be asking why did I not just use fabric, paver, or pyopt.  Fabric and paver are nice, but their tasks were still in a single file.  The project for which we use newman has lots of task modules.  Organization of many tasks was one of the main goals.  On the surface I didn't see an easy way to do it in the other tools.

Newman also has an advanced feature that allows you to import it and make use of its argparse wrapper.  This gives you the ability to use it to bundle up multiple task modules and ship it as a command line tool.  I will go more in-depth in a following blog post.
