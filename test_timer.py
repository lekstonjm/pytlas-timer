from sure import expect
from pytlas.testing import create_skill_agent
import os
import timer

class TestTimer:
    def setup(self):
        self.agent = create_skill_agent(os.path.dirname(__file__))
        self.agent.model.reset()
    
    def test_help_on_skill(self):
        self.agent.parse("what is timer skill")
        call = self.agent.model.on_answer.get_call(0)
        expected_response = "Timer skill {0} countdown time for you to make a boiled egg a success every time. Simpy ask start a timer for 3 minutes and wait ...".format(timer.version) 
        expect(call.text).to.equal(expected_response)